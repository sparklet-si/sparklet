## 变更

模型 / 量化版本 / 硬件报告：

## 来源与复现

- 官方模型仓库与固定 commit：
- 下载地区；镜像逐文件 SHA-256 清单及清单哈希（如有）：
- 硬件、系统、驱动、运行库、Sparklet / 引擎版本：
- 上下文、输入/输出 tokens、并发、KV 格式、测量方法：
- 可公开的测试证据（Issue / Discussion / 报告）：

## 检查

- [ ] 一个量化变体一个模型文件，一组环境一个实测文件。
- [ ] 未知数据用 null；失败和 OOM 如实记录，不把估算写成实测。
- [ ] Windows UMA 分别记录安装、可见、专用、共享、进程预算和系统提交口径。
- [ ] 不包含模型权重、凭据、内网地址、私有路径或原始内部日志。
- [ ] 已增加 catalog/catalog.json 的 sequence，并运行 `python3 tools/catalog.py` 与 `python3 -m unittest discover -s tools -v`。
- [ ] 新生成文件已加入 PR，旧 objects 文件未修改或删除。
