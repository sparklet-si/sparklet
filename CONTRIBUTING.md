# 推荐目录贡献

欢迎通过 Fork → 分支 → Pull Request 提交模型资料、下载源与硬件实测。产品源码暂不开放；此流程只维护公开推荐数据与校验工具，不接收产品源码、权重或内部日志。

1. 复制 `catalog/models/` 中一个文件，按 `schemas/model.schema.json` 填写。每个固定模型版本 / 量化变体使用稳定、唯一的 ID。模型名称、简介、格式、全球/中国大陆来源分别维护。无可靠数据使用 `null` 或空列表，不写 0 代替未知。
2. 实测放在 `catalog/reports/<model-id>/<report-id>.json`，遵守 `schemas/report.schema.json`，并从模型的 `hardware[].reportIds` 引用。不同 OS、驱动、分区、引擎或版本建立不同报告，报告最多 32 个上下文测量点；更多点拆文件。新增硬件可直接增加 hardware 条目。
3. 提供公开复现证据，记录输入与输出长度、上下文容量、并发、批量、KV 格式、重复次数、持续时间、预填充和生成吞吐的独立计时。单次请求总耗时不能直接当作 decode TPS。内存容量使用 GiB，文件大小使用 bytes（UI 显示 GB）；列出进程 GPU、进程 RSS、全机专用区与系统提交的各自峰值及采样方法。
4. 全球下载源固定到上游 commit。中国大陆镜像不得仅凭同名视作同一文件：须给出 HTTPS 逐文件 SHA-256 清单和清单自身 SHA-256；维护者核对它与固定上游版本一致后合并。目录的地区链接用于手动下载；程序的自动权重下载仍经过内置来源和格式校验。
5. 增加 `catalog/catalog.json` 中的整数 `sequence`，更新 `updatedAt`，运行 `python3 tools/catalog.py` 和 `python3 -m unittest discover -s tools -v`。把生成的 `catalog/v1/index.json` 与新增 `objects/` 文件一起提交；保留旧对象，以便已有客户端按旧索引取回详情。

CI 验证字段、跨文件引用、版本固定、镜像校验信息、UMA 口径、大小限制、生成结果与版本递增。CI 不会下载权重、运行社区命令或自动证明性能；维护者仍需审核模型授权、来源可信度、镜像文件一致性和硬件结论。

`tested` 表示报告中存在通过的测试点，不能扩展为所有上下文或并发都能运行；`failed` 需要失败报告，`unverified` 表示尚无可用结论。报告保留失败点，不将 OOM 点外推为可用配置。

## 合并规则（仓库管理员配置）

`main` 的 ruleset 要求通过 PR；至少一名维护者批准；新提交撤销旧批准；最近一次推送由他人批准、对话全部解决、分支最新；必须通过 `catalog-validation`；禁止强推与删除分支。`.github/CODEOWNERS` 指定有仓库写权限的维护者 `@dionren`，并要求 Code Owner 审核。工作流、Schema、校验器、下载域名变更同样由维护者复核。

不设置绕过规则的账号。当前只有一名 Code Owner，维护者自己的 PR 需要另一名有写权限的 Code Owner 审核；扩充维护团队时先由仓库管理员配置真实成员权限和 CODEOWNERS，不能自行批准自己的 PR。

使用 squash merge。冲突时重新基于 main 生成目录并递增 sequence。不要启用自动批准或无人工审核的自动合并。目录数据合并后由 GitHub raw 提供，客户端在下一次检查时获取；目录不创建程序 Release，也不修改产品版本。需要撤回时提交新的更大 sequence，删除当前索引中的条目，保留旧对象；不改写已分发的对象。

工作流仅使用 `pull_request` 的只读权限，检出时不保留凭据，不使用 `pull_request_target` 执行贡献者代码。首次外部贡献可能需要维护者批准运行 CI。ruleset 和团队是 GitHub 仓库设置，放入这些文件不会自动启用它们。
