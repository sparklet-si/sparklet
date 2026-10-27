#!/usr/bin/env python3
"""Public catalog validator/builder. Standard library only; never downloads weights."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 64 * 1024
INDEX_LIMIT = 32 * 1024
ID = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def read(path):
    require(not path.is_symlink(), f"symlink forbidden: {path}")
    require(path.stat().st_size <= LIMIT, f"file exceeds 64 KiB: {path}")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda value: require(False, f"invalid number: {value}"))


def shape(value, schema, where="$"):
    """Validate the deliberately small JSON Schema subset used by this catalog."""
    supported = {"$schema", "title", "description", "type", "properties", "required", "additionalProperties",
                 "items", "minItems", "maxItems", "minLength", "maxLength", "pattern", "enum", "const", "minimum", "maximum"}
    require(not set(schema) - supported, f"unsupported schema keyword: {where}")
    types = schema.get("type", [])
    types = [types] if isinstance(types, str) else types
    checks = {"object": isinstance(value, dict), "array": isinstance(value, list), "string": isinstance(value, str),
              "number": type(value) in (int, float) and math.isfinite(value), "integer": type(value) is int,
              "boolean": type(value) is bool, "null": value is None}
    require(not types or any(checks.get(t, False) for t in types), f"{where}: expected {types}")
    if "enum" in schema:
        require(value in schema["enum"], f"{where}: invalid value")
    if "const" in schema:
        require(value == schema["const"], f"{where}: wrong constant")
    if isinstance(value, dict):
        require(set(schema.get("required", [])) <= value.keys(), f"{where}: missing required fields")
        props = schema.get("properties", {})
        require(schema.get("additionalProperties", True) or not value.keys() - props.keys(), f"{where}: unknown fields")
        for key, item in value.items():
            if key in props:
                shape(item, props[key], f"{where}.{key}")
    if isinstance(value, list):
        require(schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", 10000), f"{where}: array size")
        for i, item in enumerate(value):
            shape(item, schema.get("items", {}), f"{where}[{i}]")
    if isinstance(value, str):
        require(schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", LIMIT), f"{where}: text length")
        require("pattern" not in schema or re.search(schema["pattern"], value), f"{where}: invalid text")
    if type(value) in (int, float):
        require(math.isfinite(value) and schema.get("minimum", -math.inf) <= value <= schema.get("maximum", math.inf), f"{where}: number out of range")


def public_url(value):
    url = urlsplit(value)
    require(url.scheme == "https" and url.hostname and "." in url.hostname and not url.username and not url.password
            and not url.query and not url.fragment and url.port in (None, 443), f"expected public HTTPS URL without credentials/query/fragment: {value}")
    import ipaddress
    try:
        ipaddress.ip_address(url.hostname)
    except ValueError:
        require(not url.hostname.endswith((".local", ".internal", ".localhost")), "private hostname")
    else:
        raise ValueError("IP addresses are not catalog download/evidence sources")


def load(root):
    config = read(root / "catalog/catalog.json")
    require(set(config) == {"schemaVersion", "sequence", "updatedAt"} and type(config["schemaVersion"]) is int and config["schemaVersion"] == 1, "invalid catalog config")
    require(type(config["sequence"]) is int and 0 < config["sequence"] < 2**53, "invalid sequence")
    from datetime import date
    require(date.fromisoformat(config["updatedAt"]).isoformat() == config["updatedAt"], "updatedAt must be YYYY-MM-DD")
    schemas = {kind: read(root / f"schemas/{kind}.schema.json") for kind in ("model", "report")}
    models, reports = {}, {}
    for kind, target, glob in [("model", models, "models/*.json"), ("report", reports, "reports/*/*.json")]:
        for path in sorted((root / "catalog").glob(glob)):
            require(path.resolve().is_relative_to(root.resolve()), "catalog input escapes root")
            value = read(path)
            shape(value, schemas[kind], str(path))
            require(ID.fullmatch(value["id"]), "invalid id")
            require(path.stem == value["id"] and value["id"] not in target, "duplicate/mismatched id")
            if kind == "report":
                require(path.parent.name == value["modelId"], "report directory differs from modelId")
            target[value["id"]] = value
    require(models, "empty catalog")
    for model in models.values():
        require(all(part not in (".", "..") for part in model["source"]["repo"].split("/")), "invalid repository")
        revision = model["source"]["revision"]
        require(SHA.fullmatch(revision), "model revision must be a complete commit SHA")
        require(model["downloads"]["global"], "at least one global download source required")
        for links in model["downloads"].values():
            for link in links:
                public_url(link["url"])
                require(link["revision"] == revision, "mirror revision differs from canonical model")
                require(link["verification"] in ("upstream", "sha256-manifest"), "mirror verification required")
                if link["verification"] == "upstream":
                    require(link["url"] == f'https://huggingface.co/{model["source"]["repo"]}/tree/{revision}', "upstream URL must pin canonical revision")
                else:
                    require(link["manifestUrl"] and re.fullmatch(r"[0-9a-f]{64}", link["manifestSha256"] or ""), "mirror needs file SHA-256 manifest")
                    public_url(link["manifestUrl"])
        hardware_ids = set()
        all_reports = [rid for h in model["hardware"] for rid in h["reportIds"]]
        require(len(all_reports) <= 256 and len(all_reports) == len(set(all_reports)), "duplicate/too many model reports")
        for hardware in model["hardware"]:
            require(hardware["id"] not in hardware_ids, "duplicate hardware target")
            hardware_ids.add(hardware["id"])
            selected = []
            for report_id in hardware["reportIds"]:
                report = reports.get(report_id)
                require(report and report["modelId"] == model["id"] and report["hardwareId"] == hardware["id"], "missing or mismatched report")
                selected.append(report)
            outcomes = {s["outcome"] for r in selected for s in r["samples"]}
            require(hardware["status"] != "tested" or "pass" in outcomes, "tested status needs a passing report")
            require(hardware["status"] != "failed" or outcomes & {"oom", "error"}, "failed status needs evidence")
            require(hardware["status"] == "unverified" or selected, "hardware status requires evidence")
    for report in reports.values():
        model = models.get(report["modelId"])
        require(model and report["revision"] == model["source"]["revision"], "report model/revision mismatch")
        require(any(report["id"] in h["reportIds"] for h in model["hardware"]), "orphan report")
        for url in report["evidence"]:
            public_url(url)
        from datetime import date
        require(date.fromisoformat(report["testedAt"]).isoformat() == report["testedAt"], "testedAt must be YYYY-MM-DD")
        env = report["environment"]
        if env["memoryArchitecture"] == "windows-uma":
            require(all(env[k] is not None for k in ("installedRamGiB", "systemVisibleRamGiB", "gpuDedicatedGiB", "sharedLimitGiB", "commitLimitGiB")), "Windows UMA needs separate capacity/commit measurements")
            require(env["sharedLimitGiB"] <= env["systemVisibleRamGiB"] <= env["installedRamGiB"], "shared memory is part of visible system memory")
        for sample in report["samples"]:
            require(sample["promptTokens"] + sample["outputTokens"] <= sample["contextTokens"], "sample exceeds context capacity")
            require(sample["outcome"] == "pass" or sample["decodeTps"] is None, "failed samples must not advertise throughput")
    return config, models, reports


def build(root):
    config, models, reports = load(root)
    files = {}
    def blob(value):
        data = encode(value)
        require(len(data) <= LIMIT, "object exceeds 64 KiB; split reports/pages")
        digest = hashlib.sha256(data).hexdigest()
        files[f"objects/{digest}.json"] = data
        return {"sha256": digest, "bytes": len(data)}
    report_refs = {key: blob(value) for key, value in reports.items()}
    summaries = []
    for model in sorted(models.values(), key=lambda m: m["id"]):
        detail = dict(model)
        detail["reports"] = [{"id": rid, "hardwareId": h["id"], **report_refs[rid]} for h in model["hardware"] for rid in h["reportIds"]]
        summaries.append({key: model[key] for key in ("id", "name", "description", "format", "quantization", "source")} | {"detail": blob(detail)})
    pages, entries = [], []
    def page(items):
        return {"schemaVersion": 1, "kind": "page", "models": items}
    for summary in summaries:
        if entries and (len(entries) == 32 or len(encode(page(entries + [summary]))) > 48 * 1024):
            pages.append({"count": len(entries), **blob(page(entries))})
            entries = []
        entries.append(summary)
    if entries:
        pages.append({"count": len(entries), **blob(page(entries))})
    index = config | {"kind": "index", "modelCount": len(models), "pages": pages}
    require(len(pages) <= 128, "v1 supports at most 128 pages; introduce a new protocol for larger catalogs")
    files["index.json"] = encode(index)
    require(len(files["index.json"]) <= INDEX_LIMIT, "index exceeds 32 KiB; create a new protocol version")
    return files


def write(files, output, check=False):
    for name, data in files.items():
        path = output / name
        if check:
            require(path.is_file() and path.read_bytes() == data, f"generated file is stale: {path}")
        else:
            if name.startswith("objects/") and path.exists():
                require(path.read_bytes() == data, "immutable object conflict")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base", help="Git base SHA for monotonic sequence / immutable-object checks")
    args = parser.parse_args()
    files = build(args.root)
    write(files, args.output or args.root / "catalog/v1", args.check)
    if args.base and args.base != "0" * 40:
        import subprocess
        require(SHA.fullmatch(args.base), "base must be a complete Git SHA")
        old = subprocess.run(["git", "show", f"{args.base}:catalog/v1/index.json"], cwd=args.root, capture_output=True)
        if old.returncode == 0:
            previous = json.loads(old.stdout)
            current = json.loads(files["index.json"])
            require(previous == current or current["sequence"] > previous["sequence"], "changed catalog needs a larger sequence")
            changes = subprocess.check_output(["git", "diff", "--name-status", args.base, "--", "catalog/v1/objects"], cwd=args.root, text=True)
            require(all(line.startswith("A\t") for line in changes.splitlines()), "published objects cannot be edited or removed")
    for path in (args.root / "catalog/v1/objects").glob("*.json"):
        data = path.read_bytes()
        require(len(data) <= LIMIT and path.stem == hashlib.sha256(data).hexdigest(), "invalid immutable object")
    print(f"Catalog valid: {len(files)} files, largest {max(map(len, files.values()))} bytes")


if __name__ == "__main__":
    main()
