# 128 GiB DGX Spark 推荐模型研究

审核日期：**2026-10-27**。目录序号：**2026102702**。面向一台 Linux ARM64 / NVIDIA GB10 / 128 GiB 统一内存设备；不外推到 Windows RTX Spark。本文只收录公开信息。

此次新增 24 条，保留并重新定位原有 4 条，共 **28 个固定版本/量化变体**。其中 19 条来自中国模型团队，9 条来自其他团队。排序先满足中国团队优先，再综合用途、质量、活跃度、单流延迟、内存余量和部署成熟度；不是把不同任务的模型放进统一跑分榜。NVIDIA 发布的 Qwen 量化仍归入中国组。

2026-10-28 目录修订：撤回 gpt-oss 20B MXFP4 推荐，目录序号更新为 `2026102801`，保留 27 条。下文保留 2026-10-27 的研究快照；该模型的链接指向历史对象，不表示仍在当前推荐列表中。

2026-10-31 目录修订：新增 [Nemotron 3.5 Transcribe 30B-A4B · NVFP4](catalog/models/nemotron-3.5-transcribe-30b-a4b-nvfp4.json)，目录序号 `2026103101`，当前共 28 条。它是 2026-10-28 发布的语音专项模型（SALM：Nemotron 3.5 Lightning 混合 Mamba-Transformer MoE 主干加并行专家音频编码器），覆盖 40 种语言转写、语音翻译、说话人区分和音频问答；固定 revision `66c6adc4020179567074d0399cda2a4eeb2bb347`，仓库更新 2026-10-29，授权元数据 `openmdw-1.1`，选中 17 个文件共 21.58 GB，审核日近 30 天下载 1,940。国际组 rank 50，位于 Nemotron 3.5 Super VL 之后、Gemma 4 之前；与 Qwen3-ASR、FireRedASR2 一样按专项任务入选，不与聊天模型比较。

同日扩展模型优化工作台资料，目录序号增加至 `2026103102`：源目录共 29 个变体，v1 仍有 28 个推荐条目。原 Nemotron Transcribe 条目明确为无 DFlash / 无 MTP 的常规解码；另增 [DFlash2 配置](catalog/models/nemotron-3.5-transcribe-30b-a4b-nvfp4-dflash2.json)，暂不推荐，两个配置均为待优化、尚无 Sparklet 实测。目标权重 revision 相同，草稿固定为 `4172ee5b7bfe55f59e784922878c1bd9bdfeb6ba`；草稿选取 `LICENSE`、`THIRD_PARTY_NOTICES.md`、`config.json`、`licenses/vLLM-LICENSE.txt` 和 `model.safetensors`，共 1,141,314,162 字节，与目标文件合计 22,718,272,100 字节。草稿是额外依赖，不单独用于转写。DFlash2 不提供 CTC 词级时间戳；延迟收益随音频长度与并发而变，官方 NIM 优化不能当作开源环境或 Sparklet 的实测成绩。依据：[固定草稿模型卡](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2/blob/4172ee5b7bfe55f59e784922878c1bd9bdfeb6ba/README.md)及上述固定目标模型卡。

入选与边界：模型卡在 Open ASR 英文 9 集平均 WER 4.71、长音频 10.98、7 语言多语 4.62 均为所列开源模型最佳；这些是 BF16 结果，卡片说明 NVFP4 平均错误率相对高约 3.6%。官方路线需要 vLLM 0.32.0 与 NeMo Speech main 的 `nemo_speechlm` 插件，参考部署为单卡 96 GB RTX PRO 6000；兼容表列出 DGX Spark (GB10) NVFP4，但仅限 Linux / WSL2，原生 Windows 只列 GGML。同系列的 [DFlash2](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2) 约 570M 参数，是只能配合本模型使用的投机解码草稿，与内置 MTP 二选一且不支持词级时间戳，草稿本身不作为独立转写模型；无 DFlash 条目不计入草稿下载，DFlash2 组合条目另计该依赖。BF16 / FP8 变体暂未收录，理由同 Qwen3.8 的单一 NVFP4 主推荐。DGX Spark 状态保持 `unverified`。

## 判断方法与边界

1. 查阅模型开发者的模型卡、固定 commit 文件目录、官方引擎文档、引擎维护者基准、社区部署仓库和原作者实测。搜索覆盖 Qwen、GLM、DeepSeek、Kimi、MiniMax、Step、Hunyuan、LongCat、Nemotron、gpt-oss、Gemma、Mistral；以文本/多模态生成、语音识别、OCR 为范围。
2. 活跃度结合近期发布/更新、近 30 天仓库下载、维护中的 GB10 配方。下载数是 Hugging Face API 的审核日快照，量化仓库与原模型仓库分别统计；它不是用户数、质量分数或性能指标。旧模型若仍被大量使用，可以作为成熟兼容路线保留；FireRed 和 0.6B 明确保留作专项/入门用途。
3. 从上游 API 的完整 40 位 revision 和逐文件 size 建立 `curation.files`。下载体积使用十进制 GB；内存讨论用 GiB。该清单记录元数据，不意味着已下载并逐字节验算模型。固定版本的所有选中文件须复核存在且大小一致；不把同仓库全部量化相加。
4. 128 GiB 是安装容量，不是模型可独占预算。初筛时优先给系统、加载临时缓冲、CUDA graph、KV cache 和视觉编码保留余量；本轮以至少约 12–16 GiB 作为**编辑筛选的余量目标**，不是运行时自动配置或容量保证。约 90 GiB 以上的存储折算权重及特殊卸载方案列为有条件备选。统一内存中的 CPU/GPU 驻留不能重复相加，磁盘映射也不能当作免费内存。
5. 本文给出的 4K/8K、并发 1 是开始验证的建议。模型标称最大上下文、其他机器的负载或示例中的高并发不能直接照搬。未取得符合目录协议的同模型 revision、同量化、同引擎完整实测报告，因此所有 DGX 条目仍为 `unverified`，GPU/系统内存实测值仍为 `null`，不生成伪造的 TPS 或硬件报告。
6. “有容量/社区依据的候选”与“当前 Sparklet 可登记”分开。当前 Sparklet 的原生适配范围内有 8 条；另外 20 条需要外部引擎，目录不会因此安装引擎、下载权重或加载模型。没有核验过的中国大陆镜像继续留空。

## 推荐顺序

“组件可匹配”只表示当前 Sparklet 有对应架构/格式，GGUF 还依赖服务构建能力；不是目标硬件验收。“外部引擎”可在详情中查看具体要求。所列大小包括 `curation.files` 中的全部文件；Gemma 4、Step 的条目包括指定视觉 projector，其他投机解码草稿均未计入。

| 顺序 | 来源 | 模型/量化（完整元数据） | 文件 GB | 近 30 天仓库下载 | Sparklet 登记 |
| ---: | :---: | --- | ---: | ---: | --- |
| 1 | CN | [Qwen3.8 27B · NVIDIA NVFP4](catalog/models/qwen3.8-27b-nvfp4.json) | 21.94 | 369,240 | 需外部引擎 |
| 2 | CN | [Qwen3.6 35B-A3B · NVIDIA NVFP4](catalog/models/qwen3.6-35b-a3b-nvfp4.json) | 23.46 | 4,153,731 | 需外部引擎 |
| 3 | CN | [Qwen3-Coder-Next · 官方 Q4_K_M](catalog/models/qwen3-coder-next-q4-k-m.json) | 48.41 | 46,020 | 需外部引擎 |
| 4 | CN | [GLM-4.7-Flash · Q4_K_M](catalog/models/glm-4.7-flash-q4-k-m.json) | 18.31 | 240,946 | 需外部引擎 |
| 5 | CN | [Qwen3.5 9B · BF16](catalog/models/qwen3.5-9b-bf16.json) | 19.33 | 6,184,812 | 需外部引擎 |
| 6 | CN | [Qwen3 14B · BF16](catalog/models/qwen3-14b-bf16.json) | 29.55 | 11,433,704 | 组件可匹配 |
| 7 | CN | [Qwen3 8B · BF16](catalog/models/qwen3-8b-bf16.json) | 16.40 | 8,265,514 | 组件可匹配 |
| 8 | CN | [Qwen3 4B Instruct 2507 · BF16](catalog/models/qwen3-4b-instruct-2507-bf16.json) | 8.06 | 2,653,004 | 组件可匹配 |
| 9 | CN | [Qwen3 32B · BF16](catalog/models/qwen3-32b-bf16.json) | 65.54 | 2,878,593 | 组件可匹配 |
| 10 | CN | [Qwen3.5 122B-A10B · NVIDIA NVFP4](catalog/models/qwen3.5-122b-a10b-nvfp4.json) | 83.53 | 196,375 | 需外部引擎 |
| 11 | CN | [Qwen3-ASR 1.7B · BF16](catalog/models/qwen3-asr-1.7b-bf16.json) | 4.70 | 1,389,419 | 需外部引擎 |
| 12 | CN | [GLM-OCR · BF16](catalog/models/glm-ocr-bf16.json) | 2.66 | 1,745,838 | 需外部引擎 |
| 13 | CN | [Qwen3.8-Flash-Next · NVIDIA FP4-Local](catalog/models/qwen3.8-flash-next-fp4-local.json) | 102.26 | 18,029 | 需外部引擎 |
| 14 | CN | [Step-3.7-Flash · 官方 Q3_K_L](catalog/models/step-3.7-flash-q3-k-l.json) | 106.48 | 5,739 | 需外部引擎 |
| 15 | CN | [MiniMax M2.7 · UD-Q3_K_M](catalog/models/minimax-m2.7-ud-q3-k-m.json) | 101.24 | 5,428 | 需外部引擎 |
| 16 | CN | [FireRedASR2-LLM](catalog/models/fireredasr2-llm.json) | 18.87 | 345 | 组件可匹配 |
| 17 | CN | [Qwen3 0.6B](catalog/models/qwen3-0.6b.json) | 1.52 | 24,034,480 | 组件可匹配 |
| 18 | CN | [Qwen3.8-Flash-Next · Bartowski Q2_K](catalog/models/qwen3.8-flash-next-q2-k.json) | 80.93 | 96,102 | 组件可匹配 |
| 19 | CN | [Qwen3.8-Flash-Next · Unsloth UD-Q4_K_XL](catalog/models/qwen3.8-flash-next-ud-q4-k-xl.json) | 111.33 | 1,064,465 | 组件可匹配 |
| 20 | US | [Nemotron 3.5 Lightning 30B-A3B · NVFP4](catalog/models/nemotron-3.5-lightning-nvfp4.json) | 21.58 | 1,064,946 | 需外部引擎 |
| 21 | US | [gpt-oss 120B · 官方 MXFP4](catalog/models/gpt-oss-120b-mxfp4.json) | 65.28 | 2,857,039 | 需外部引擎 |
| 22 | US | [Nemotron 3.5 Bolt 74B-A9B · 24GB IQ2](catalog/models/nemotron-3.5-bolt-74b-a9b-24gb.json) | 24.12 | 10,877 | 需外部引擎 |
| 23 | US | [Nemotron 3.5 Super VL 120B-A12B · NVFP4](catalog/models/nemotron-3.5-super-vl-nvfp4.json) | 75.06 | 23,207 | 需外部引擎 |
| 24 | US | [gpt-oss 20B · 官方 MXFP4（已撤回）](catalog/v1/objects/662a76c700c3fe9cbe794f6eef39c205f5131d25cd034288401116f21763dc12.json) | 13.79 | 5,891,996 | 需外部引擎 |
| 25 | US | [Gemma 4 26B-A4B · UD-Q4_K_M](catalog/models/gemma-4-26b-a4b-ud-q4-k-m.json) | 18.14 | 1,120,578 | 需外部引擎 |
| 26 | US | [Gemma 4 31B · Q4_K_M](catalog/models/gemma-4-31b-q4-k-m.json) | 19.52 | 270,457 | 需外部引擎 |
| 27 | US | [Nemotron 3 Nano 30B-A3B · NVFP4](catalog/models/nemotron-3-nano-30b-a3b-nvfp4.json) | 19.36 | 1,335,074 | 需外部引擎 |
| 28 | FR | [Mistral Small 4 119B · 官方 NVFP4](catalog/models/mistral-small-4-nvfp4.json) | 70.85 | 2,828 | 需外部引擎 |

## 选择理由

- **通用与编程主候选**：Qwen3.8-27B NVFP4 放在首位，兼顾中文、代码、视觉和相对宽裕的容量；Qwen3.6-35B-A3B 作为低延迟 MoE 方向；Qwen3-Coder-Next 保留官方 Q4_K_M 供编程专用。GLM-4.7-Flash 为活跃的轻量中国模型替代。这里的优先级是本次编辑判断，不能证明在每个任务上胜出。
- **现有 Sparklet 路线**：Qwen3 14B、8B、4B Instruct 2507、32B 使用官方未量化 safetensors，覆盖质量与响应速度的取舍；对普通 attention 路径从 4K 起步。没有将同架构的所有小尺寸重复列入。0.6B 保留作快速下载与开发检查，FireRed 保留作语音专项。
- **语音与文档**：Qwen3-ASR-1.7B 与 GLM-OCR 按各自任务入选。它们体积较小，有活跃的官方仓库；文本聊天指标不适用于这些模型，当前 Sparklet 也没有对应组件。
- **大模型有条件备选**：Qwen3.5-122B NVFP4 保留给可接受较高占用的任务。Qwen3.8 FP4-Local 有 NVIDIA 单 Spark 配方，但依赖特殊 scale 格式、PLE 支持及指定社区容器。Step-3.7 Q3_K_L 有开发者的同量化 GB10 基准；MiniMax M2.7 UD-Q3_K_M 是容量/量化损失折中。原有 Qwen3.8 Q2_K 与 UD-Q4_K_XL 保留为已有集成选项，移到中国组末尾并写清限制。
- **国际模型**：Nemotron 3.5 Lightning 有明确单机 GB10 配方，作为高效英语/代理方向；gpt-oss-120B 原生 MXFP4 保留较大内存余量。新发布的 Bolt 24GB 和 Super VL 都有官方/社区单 Spark 路线，但需匹配专用内核、模型代码与草稿配置。gpt-oss-20B 为低占用选择；Gemma 4 的 26B-A4B 与 31B 对应稀疏/稠密不同取舍；Nano 3 保留作成熟基线。Mistral Small 4 的文件容量合理，但单机性能证据较弱，放在国际组后部并注明官方示例为双 GPU。

## 社区证据如何使用

### 引擎维护者的原始基准

[llama.cpp 的 DGX Spark 基准](https://github.com/ggml-org/llama.cpp/blob/master/benches/dgx-spark/dgx-spark.md)分别测量 prompt processing 与 token generation，并提供随历史长度变化的结果。举例：无额外历史的 `tg32` 测量中，ggml-org 的 gpt-oss-20B MXFP4 为 83.43 ± 0.59 token/s，120B 为 58.72 ± 0.20，GLM-4.7-Flash **Q8_0** 为 48.68 ± 0.12。它们是短输出微基准；不是应用端到端吞吐。表中 ggml-org GGUF 不等于本目录的 OpenAI safetensors 或 Unsloth Q4_K_M，故这些数字仅用于判断模型家族在 GB10 上有实际运行基础，不填入目录 reports。

### 同机器类型的场景差异

[Qwen3.8-27B 原作者测试](https://github.com/HAOyezi/qwen38-27b-dgx-spark-benchmarks)记录 2026-09-05 至 09-08 的单台 GX10、Ubuntu 24.04.4、驱动 580.173.02，不同引擎/精度/负载。其 vLLM NVFP4 长提示缓存场景报告约 24 token/s；SGLang + DFlash2 的代码生成报告 38.6，而短对话为 15.9。报告中的 16 并发聚合吞吐与单用户解码不是同一指标。其部分量化还经过微调，因此不能把跨变体比较当成受控精度实验；本目录只采用“核对量化、引擎和场景，不把最快数字普遍化”的结论。

### 持续维护的部署配方

[eugr/spark-vllm-docker](https://github.com/eugr/spark-vllm-docker)提供单机与集群路线，包含 Qwen3.8-27B、Flash-Next FP4-Local、Nemotron 3.5 等。逐条检查 `solo` / TP 设置、依赖和实验性标记；不会把双 Spark 配方认成单机。其 GLM-5.3 Flash b12x 配方明确仍属实验性；这一点降低其本轮主推荐优先级。

[NVIDIA DGX Spark playbooks](https://github.com/NVIDIA/dgx-spark-playbooks)与 NVIDIA 量化模型卡用于核对平台和部署前提。特别注意：Nemotron Lightning 的 `*-DSpark` 是投机解码草稿，不能作为独立目标模型；Flash-Next FP4-Local 的模型卡明确要求指定容器，不能假定普通上游 vLLM 已支持。

[wesche 的原始比较](https://wesche.com/dgx/)提供不同任务的质量观察，同时区分一台、两台和四台 Spark、挑战集与完整集。它的评分方法有版本，不能拼接不同时期的分数；DeepSeek 专用 DS4 路径的成功也不能迁移成普通 GGUF 或 Sparklet 已支持的结论。本文未用这些异构分数构造统一排行榜。

## 已研究但暂未纳入的方向

| 方向 | 本轮判断 |
| --- | --- |
| [DeepSeek V4.1 Flash 1017](https://huggingface.co/unsloth/DeepSeek-V4.1-Flash-1017-GGUF/tree/60ad3651641b5c97679c807e064ab1d7a3ca1455) | 本次核对的 Unsloth UD-Q2_K_XL 文件总量约 334.79 GB，含巨大的专用表，不能按普通全驻留 GGUF 路径推荐。旧版 V4 Flash 的单 Spark DS4/专用卸载结果不是该 revision 的证明；继续观察专用格式、卸载与持续运行证据，并非宣称这类模型永远不能单机运行。 |
| [GLM-5.3-Flash](https://huggingface.co/unsloth/GLM-5.3-Flash-GGUF/tree/a38483c8cd5df544f53d70fb281afe97369d5ab6) | 官方源文件约 328 GB；Unsloth UD-Q2_K_XL 约 108.72 GB，存储折算约 101.25 GiB，理论容量不能证明运行峰值、长上下文或 2-bit 质量。社区 b12x 正在实验；当前以 GLM-4.7-Flash 为更稳妥主推荐，等待新架构同版本可复现报告。 |
| [MiniMax M3.1 Flash](https://huggingface.co/unsloth/MiniMax-M3.1-Flash-GGUF/tree/b17b7f5459c0b8f127ea12ee774409b282521d6a) | 2026-10-26 新近更新，Unsloth UD-Q2_K_XL 已约 143.91 GB，仅文件就超过 128 GiB 的全驻留容量。M2.7 Q3 作为当前有条件折中，不把 M3.1 新发布等同于本机适合。 |
| Kimi K3、完整大型 Kimi / GLM / Qwen / Step 旗舰 | 活跃但大参数原版没有在本轮建立可审查的单台 128 GiB 完整部署证据；多机、极低比特、磁盘卸载必须按各自精确版本评估。保留为后续研究，不能仅按每 token 激活参数计算权重容量。 |
| Hunyuan、LongCat 与社区衍生微调 | 搜索覆盖其官方仓库；本轮优先覆盖已有明确用途与活跃证据的代表型号，避免把相似变体填满目录。HunyuanOCR 可作为后续专项扩展；大型 LongCat 及稀疏专用格式仍需核对实际后端。 |
| Qwen3.8 FP8 / BF16、同系列所有量化 | 128 GiB 放得下不代表单流更快；优先一条 NVFP4 主推荐，避免未经受控对比就将高精度宣传为更适合。用户需要精度对照时可再增加对应变体。 |
| DSpark、DFlash、MTP、LiLiCorr 单独仓库 | 它们是配套草稿/辅助组件，不是独立聊天模型，不应占一个主推荐型号。若配方使用，必须另外计算下载与运行内存。 |

以上结论只约束本轮推荐，不改变已有用户模型。各下载源的许可证以固定上游版本为准，不能因为某个系列通常使用 Apache/MIT 就覆盖 Qwen Community、NVIDIA Open Model Agreement、OpenMDW 或 Modified MIT 的具体条款。

## 每条固定版本的证据

每项首个链接固定到所选仓库 revision 的模型卡；后续链接为开发者或实测作者的公开资料，可能继续更新。精确文件路径、字节数和证据同存于对应 `catalog/models/*.json` 的 `curation`。以下更新时间仅为仓库更新，不等于模型首次发布日期。

1. **Qwen3.8 27B · NVIDIA NVFP4**：`482ca0f3832238542f8f5295dde86b5f22711d80`；仓库更新 2026-09-17；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/blob/482ca0f3832238542f8f5295dde86b5f22711d80/README.md) · [资料 2](https://github.com/HAOyezi/qwen38-27b-dgx-spark-benchmarks) · [资料 3](https://github.com/eugr/spark-vllm-docker)
2. **Qwen3.6 35B-A3B · NVIDIA NVFP4**：`1355db6a052410cfd62085d94b58866fd0f2c3c5`；仓库更新 2026-08-29；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/nvidia/Qwen3.6-35B-A3B-NVFP4/blob/1355db6a052410cfd62085d94b58866fd0f2c3c5/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
3. **Qwen3-Coder-Next · 官方 Q4_K_M**：`b82fb7382639d97b38fa7672e526c760c2fb358e`；仓库更新 2026-02-04；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/Qwen/Qwen3-Coder-Next-GGUF/blob/b82fb7382639d97b38fa7672e526c760c2fb358e/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
4. **GLM-4.7-Flash · Q4_K_M**：`0d32489ecb9db6d2a4fc93bd27ef01519f95474d`；仓库更新 2026-02-12；授权元数据 `mit`。[资料 1](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF/blob/0d32489ecb9db6d2a4fc93bd27ef01519f95474d/README.md) · [资料 2](https://huggingface.co/zai-org/GLM-4.7-Flash) · [资料 3](https://github.com/ggml-org/llama.cpp/blob/master/benches/dgx-spark/dgx-spark.md)
5. **Qwen3.5 9B · BF16**：`c202236235762e1c871ad0ccb60c8ee5ba337b9a`；仓库更新 2026-03-02；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/Qwen/Qwen3.5-9B/blob/c202236235762e1c871ad0ccb60c8ee5ba337b9a/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
6. **Qwen3 14B · BF16**：`40c069824f4251a91eefaf281ebe4c544efd3e18`；仓库更新 2025-07-26；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/Qwen/Qwen3-14B/blob/40c069824f4251a91eefaf281ebe4c544efd3e18/README.md)
7. **Qwen3 8B · BF16**：`b968826d9c46dd6066d109eabc6255188de91218`；仓库更新 2025-07-26；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/README.md)
8. **Qwen3 4B Instruct 2507 · BF16**：`cdbee75f17c01a7cc42f958dc650907174af0554`；仓库更新 2025-09-17；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/cdbee75f17c01a7cc42f958dc650907174af0554/README.md)
9. **Qwen3 32B · BF16**：`9216db5781bf21249d130ec9da846c4624c16137`；仓库更新 2025-07-26；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/Qwen/Qwen3-32B/blob/9216db5781bf21249d130ec9da846c4624c16137/README.md)
10. **Qwen3.5 122B-A10B · NVIDIA NVFP4**：`98915d837c4e7c87ac8296d02e89de19b3207e6d`；仓库更新 2026-06-02；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/nvidia/Qwen3.5-122B-A10B-NVFP4/blob/98915d837c4e7c87ac8296d02e89de19b3207e6d/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
11. **Qwen3-ASR 1.7B · BF16**：`7278e1e70fe206f11671096ffdd38061171dd6e5`；仓库更新 2026-01-30；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/Qwen/Qwen3-ASR-1.7B/blob/7278e1e70fe206f11671096ffdd38061171dd6e5/README.md) · [资料 2](https://github.com/QwenLM/Qwen3-ASR)
12. **GLM-OCR · BF16**：`2e85a62840ccac27daa451df36c736c4636b8628`；仓库更新 2026-09-11；授权元数据 `mit`。[资料 1](https://huggingface.co/zai-org/GLM-OCR/blob/2e85a62840ccac27daa451df36c736c4636b8628/README.md) · [资料 2](https://github.com/zai-org/GLM-OCR)
13. **Qwen3.8-Flash-Next · NVIDIA FP4-Local**：`b9ce18a6887e18c089fdea8509a33e63429a3300`；仓库更新 2026-10-15；授权元数据 `nvidia-open-model-agreement`。[资料 1](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local/blob/b9ce18a6887e18c089fdea8509a33e63429a3300/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
14. **Step-3.7-Flash · 官方 Q3_K_L**：`0b69336d2fd2adfdef9c66e425f7778196c31482`；仓库更新 2026-06-03；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/stepfun-ai/Step-3.7-Flash-GGUF/blob/0b69336d2fd2adfdef9c66e425f7778196c31482/README.md)
15. **MiniMax M2.7 · UD-Q3_K_M**：`d2a05ccf69491b03db0cc40b335aec14bdaf7198`；仓库更新 2026-04-14；授权元数据 `modified-mit`。[资料 1](https://huggingface.co/unsloth/MiniMax-M2.7-GGUF/blob/d2a05ccf69491b03db0cc40b335aec14bdaf7198/README.md) · [资料 2](https://huggingface.co/MiniMaxAI/MiniMax-M2.7)
16. **FireRedASR2-LLM**：`2c5e0f415b9afb8f67cb8b00ea4c54959f70e824`；仓库更新 2026-03-13；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/FireRedTeam/FireRedASR2-LLM/blob/2c5e0f415b9afb8f67cb8b00ea4c54959f70e824/README.md)
17. **Qwen3 0.6B**：`c1899de289a04d12100db370d81485cdf75e47ca`；仓库更新 2025-07-26；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/README.md)
18. **Qwen3.8-Flash-Next · Bartowski Q2_K**：`db3a185731e162be9ffa4d52d20d7509939e60e8`；仓库更新 2026-10-13；授权元数据 `qwen-community-1.0`。[资料 1](https://huggingface.co/bartowski/Qwen3.8-Flash-Next-GGUF/blob/db3a185731e162be9ffa4d52d20d7509939e60e8/README.md)
19. **Qwen3.8-Flash-Next · Unsloth UD-Q4_K_XL**：`766911a6b7369840a91dbcd95f9f997acaab6cd6`；仓库更新 2026-10-06；授权元数据 `qwen-community-1.0`。[资料 1](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/blob/766911a6b7369840a91dbcd95f9f997acaab6cd6/README.md)
20. **Nemotron 3.5 Lightning 30B-A3B · NVFP4**：`bee7596271d1495f6992ae224aefde4410e816b8`；仓库更新 2026-09-10；授权元数据 `openmdw-1.1`。[资料 1](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4/blob/bee7596271d1495f6992ae224aefde4410e816b8/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
21. **gpt-oss 120B · 官方 MXFP4**：`b5c939de8f754692c1647ca79fbf85e8c1e70f8a`；仓库更新 2025-08-26；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/openai/gpt-oss-120b/blob/b5c939de8f754692c1647ca79fbf85e8c1e70f8a/README.md) · [资料 2](https://developers.openai.com/cookbook/articles/gpt-oss/run-transformers) · [资料 3](https://github.com/ggml-org/llama.cpp/blob/master/benches/dgx-spark/dgx-spark.md) · [资料 4](https://github.com/NVIDIA/dgx-spark-playbooks)
22. **Nemotron 3.5 Bolt 74B-A9B · 24GB IQ2**：`cf2effc5c4b794ee9fb8d34eab3d1d65ce64142f`；仓库更新 2026-10-20；授权元数据 `openmdw-1.1`。[资料 1](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB/blob/cf2effc5c4b794ee9fb8d34eab3d1d65ce64142f/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
23. **Nemotron 3.5 Super VL 120B-A12B · NVFP4**：`da5b2650a835292c678994a1fa3fb653250fb508`；仓库更新 2026-10-23；授权元数据 `openmdw-1.1`。[资料 1](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-NVFP4/blob/da5b2650a835292c678994a1fa3fb653250fb508/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
24. **gpt-oss 20B · 官方 MXFP4**：`6cee5e81ee83917806bbde320786a8fb61efebee`；仓库更新 2025-08-26；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/README.md) · [资料 2](https://developers.openai.com/cookbook/articles/gpt-oss/run-transformers) · [资料 3](https://github.com/ggml-org/llama.cpp/blob/master/benches/dgx-spark/dgx-spark.md)
25. **Gemma 4 26B-A4B · UD-Q4_K_M**：`c099eb48e663fd284577b04978a94ffccb261841`；仓库更新 2026-07-17；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/blob/c099eb48e663fd284577b04978a94ffccb261841/README.md) · [资料 2](https://huggingface.co/google/gemma-4-26B-A4B-it)
26. **Gemma 4 31B · Q4_K_M**：`c1ac76e99d5513b141e8adde7288b85c3f9c32ec`；仓库更新 2026-07-17；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/unsloth/gemma-4-31B-it-GGUF/blob/c1ac76e99d5513b141e8adde7288b85c3f9c32ec/README.md) · [资料 2](https://huggingface.co/google/gemma-4-31B-it)
27. **Nemotron 3 Nano 30B-A3B · NVFP4**：`6efb4a2a1c1fa277ce7b3df7a1416255011b1c99`；仓库更新 2026-08-24；授权元数据 `nvidia-nemotron-open-model-license`。[资料 1](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4/blob/6efb4a2a1c1fa277ce7b3df7a1416255011b1c99/README.md) · [资料 2](https://github.com/NVIDIA/dgx-spark-playbooks) · [资料 3](https://github.com/eugr/spark-vllm-docker)
28. **Mistral Small 4 119B · 官方 NVFP4**：`45331841b631f4e281df8e959ea3cc9beb84298a`；仓库更新 2026-09-07；授权元数据 `apache-2.0`。[资料 1](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603-NVFP4/blob/45331841b631f4e281df8e959ea3cc9beb84298a/README.md) · [资料 2](https://github.com/eugr/spark-vllm-docker)
29. **Nemotron 3.5 Transcribe 30B-A4B · NVFP4**（2026-10-31 新增）：`66c6adc4020179567074d0399cda2a4eeb2bb347`；仓库更新 2026-10-29；授权元数据 `openmdw-1.1`。[资料 1](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-NVFP4/blob/66c6adc4020179567074d0399cda2a4eeb2bb347/README.md) · [资料 2](https://github.com/NVIDIA-NeMo/Speech) · [资料 3](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)

## 维护与复查

- 复查时重新获取上游活跃度、精确 revision、选中量化文件以及社区原帖/原始仓库；不要把本日期的排名描述为长期不变的“最新”。
- 同模型新 revision 建新 ID；已有公开对象保留。修改推荐顺序也递增 catalog sequence。
- 生成前检验文件总量，生成后校验排序跨分页生效、旧 v1 可读取、未知硬件数据不被写成 0 或 tested。
- 本次是研究与目录准备；不构成模型加载、性能验收、部署或线上目录发布。
