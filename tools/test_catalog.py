import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("catalog_builder", Path(__file__).with_name("catalog.py"))
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "catalog/models").mkdir(parents=True)
        (self.root / "schemas").mkdir()
        for source in (catalog.ROOT / "schemas").glob("*.json"):
            (self.root / "schemas" / source.name).write_bytes(source.read_bytes())
        (self.root / "catalog/catalog.json").write_text(json.dumps({"schemaVersion": 1, "sequence": 1, "updatedAt": "2026-10-27"}))
        self.model = self.root / "catalog/models/fixture.json"
        self.model.write_text(json.dumps({
            "schemaVersion": 1, "kind": "model", "id": "fixture", "name": "Synthetic fixture", "description": "Synthetic fixture",
            "family": "fixture", "architecture": "fixture", "format": "safetensors", "quantization": "BF16",
            "source": {"repo": "Example/fixture", "revision": "0" * 40},
            "downloads": {"global": [{"label": "fixture", "url": "https://huggingface.co/Example/fixture/tree/" + "0" * 40,
                                      "revision": "0" * 40, "verification": "upstream", "manifestUrl": None, "manifestSha256": None}], "cn": []},
            "requirements": {"systemRamGiB": None, "gpuMemoryGiB": None, "diskBytes": 100, "notes": "Synthetic fixture"},
            "hardware": [{"id": "nvidia-rtx-spark", "name": "Synthetic fixture", "status": "unverified", "reportIds": []}]}))

    def change(self, fn):
        data = json.loads(self.model.read_text())
        fn(data)
        self.model.write_text(json.dumps(data))

    def test_deterministic_and_all_objects_integrity(self):
        files = catalog.build(self.root)
        self.assertEqual(files, catalog.build(self.root))
        index = json.loads(files["index.json"])
        self.assertEqual(index["modelCount"], 1)
        self.assertLess(len(files["index.json"]), 32768)
        for name, data in files.items():
            self.assertLessEqual(len(data), 65536)
            if name.startswith("objects/"):
                self.assertEqual(Path(name).stem, catalog.hashlib.sha256(data).hexdigest())

    def test_pages_are_bounded_and_detail_changes_reuse_other_objects(self):
        original = catalog.build(self.root)
        template = json.loads(self.model.read_text())
        for i in range(70):
            model = copy.deepcopy(template)
            model["id"] = f"example-{i}"
            (self.model.parent / f"example-{i}.json").write_text(json.dumps(model))
        generated = catalog.build(self.root)
        index = json.loads(generated["index.json"])
        self.assertEqual([p["count"] for p in index["pages"]], [32, 32, 7])
        self.assertTrue((set(original) - {"index.json"}) & set(generated))

    def test_country_then_rank_then_id_order_applies_before_pagination(self):
        template = json.loads(self.model.read_text())
        ids = []
        for i in range(35):
            model = copy.deepcopy(template)
            model["id"] = f"chinese-{i:02}"
            # The publisher of the quantized checkpoint need not be Chinese.
            model["curation"] = self.curation(rank=35 - i)
            (self.model.parent / f'{model["id"]}.json').write_text(json.dumps(model))
            ids.append(model["id"])
        self.change(lambda m: m.update(curation=self.curation(country="US", rank=1)))
        files = catalog.build(self.root)
        index = json.loads(files["index.json"])
        summaries = [m for ref in index["pages"] for m in json.loads(files[f'objects/{ref["sha256"]}.json'])["models"]]
        self.assertEqual([m["id"] for m in summaries], list(reversed(ids)) + ["fixture"])
        for summary in summaries:
            detail = json.loads(files[f'objects/{summary["detail"]["sha256"]}.json'])
            self.assertNotIn("curation", detail, "old v1 clients reject unknown detail fields")
        # Ties use stable IDs; unreviewed legacy records remain readable and last.
        self.change(lambda m: m.pop("curation"))
        self.assertEqual(sorted([
            {"id": "b", "curation": self.curation()},
            {"id": "a", "curation": self.curation()},
            json.loads(self.model.read_text()),
        ], key=catalog.recommendation_key)[0]["id"], "a")
        catalog.build(self.root)

    @staticmethod
    def curation(country="CN", rank=1):
        return {"originCountry": country, "rank": rank, "reviewedAt": "2026-10-27", "downloads30d": None,
                "evidence": ["https://example.com/model-card"], "files": [{"path": "model.safetensors", "bytes": 100}]}

    def test_curation_rejects_invalid_order_evidence_and_file_totals(self):
        self.change(lambda m: m.update(curation=self.curation()))
        original = self.model.read_bytes()
        for mutation in (
            lambda c: c.update(rank=0),
            lambda c: c.update(rank=True),
            lambda c: c.update(originCountry="cn"),
            lambda c: c.update(reviewedAt="2026-10-28"),
            lambda c: c.update(evidence=["http://example.com/model-card"]),
            lambda c: c.update(downloads30d=-1),
            lambda c: c["files"][0].update(bytes=99),
            lambda c: c["files"][0].update(path="../model.safetensors"),
            lambda c: c["files"][0].update(path="C:\\model.safetensors"),
            lambda c: c["files"].append(dict(c["files"][0])),
        ):
            self.model.write_bytes(original)
            self.change(lambda m: mutation(m["curation"]))
            with self.assertRaises(ValueError):
                catalog.build(self.root)

    def test_long_unicode_summaries_split_before_byte_limit(self):
        template = json.loads(self.model.read_text())
        for i in range(32):
            model = copy.deepcopy(template)
            model["id"] = f"unicode-{i}"
            model["description"] = "模" * 800
            (self.model.parent / f'unicode-{i}.json').write_text(json.dumps(model))
        files = catalog.build(self.root)
        pages = json.loads(files["index.json"])["pages"]
        self.assertGreater(len(pages), 1)
        self.assertEqual(sum(p["count"] for p in pages), 33)
        self.assertTrue(all(p["bytes"] <= 48 * 1024 for p in pages))

    def test_reject_unpinned_source_unsubstantiated_hardware_and_mirror(self):
        original = self.model.read_bytes()
        for mutation in (
            lambda m: m["source"].update(revision="main"),
            lambda m: m["hardware"][0].update(status="tested"),
            lambda m: m["downloads"]["global"][0].update(url="https://localhost/private"),
            lambda m: m["downloads"]["global"][0].update(verification="sha256-manifest"),
            lambda m: m["requirements"].update(gpuMemoryGiB=-1),
            lambda m: m.update(description="x" * 65536),
            lambda m: m.update(extra="not in schema"),
        ):
            self.model.write_bytes(original)
            self.change(mutation)
            with self.assertRaises(ValueError):
                catalog.build(self.root)

    def test_reject_duplicate_json_keys(self):
        self.model.write_text('{"id":"one","id":"two"}')
        with self.assertRaisesRegex(ValueError, "duplicate key"):
            catalog.build(self.root)

    def test_check_rejects_stale_generated_files(self):
        files = catalog.build(self.root)
        target = self.root / "out"
        catalog.write(files, target)
        catalog.write(files, target, True)
        (target / "index.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "stale"):
            catalog.write(files, target, True)

    def test_synthetic_uma_report_records_context_and_independent_memory(self):
        # Synthetic values exercise the contract; this is never a published benchmark.
        model = json.loads(self.model.read_text())
        report = {"schemaVersion": 1, "kind": "report", "id": "synthetic", "modelId": model["id"],
                  "hardwareId": "nvidia-rtx-spark", "revision": model["source"]["revision"], "testedAt": "2026-10-27",
                  "environment": {"os": "synthetic", "cpu": "synthetic", "gpu": "synthetic", "memoryArchitecture": "windows-uma",
                                  "installedRamGiB": 128, "systemVisibleRamGiB": 64, "gpuDedicatedGiB": 64, "sharedLimitGiB": 48,
                                  "gpuProcessBudgetGiB": 110, "commitLimitGiB": 80, "driver": "synthetic", "runtime": "synthetic",
                                  "engine": "sparklet", "engineVersion": "0.1.1", "sparkletVersion": "0.1.1", "powerMode": "synthetic", "notes": "Synthetic fixture"},
                  "method": {"throughput": "Synthetic fixture", "memory": "Synthetic fixture", "workload": "Synthetic fixture"},
                  "samples": [{"contextTokens": 4096, "promptTokens": 1024, "outputTokens": 256, "concurrency": 1, "batchSize": 1,
                               "kvCacheType": "f16", "phase": "decode", "outcome": "pass", "iterations": 3, "durationSeconds": 30,
                               "decodeTps": 12, "prefillTps": None, "ttftMs": None, "processGpuPeakGiB": 5, "processRssPeakGiB": 2,
                               "systemGpuDedicatedPeakGiB": 6, "systemCommitPeakGiB": 12, "notes": "Synthetic fixture"}],
                  "evidence": ["https://github.com/sparklet-si/sparklet/issues/1"]}
        self.change(lambda m: m["hardware"][0].update(status="tested", reportIds=["synthetic"]))
        path = self.root / f'catalog/reports/{model["id"]}/synthetic.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(report))
        catalog.build(self.root)
        for change in (lambda r: r["environment"].update(sharedLimitGiB=65),
                       lambda r: r["samples"][0].update(contextTokens=100),
                       lambda r: r["samples"][0].update(outcome="oom"),
                       lambda r: r.update(revision="1" * 40)):
            invalid = copy.deepcopy(report)
            change(invalid)
            path.write_text(json.dumps(invalid))
            with self.assertRaises(ValueError):
                catalog.build(self.root)


if __name__ == "__main__":
    unittest.main()
