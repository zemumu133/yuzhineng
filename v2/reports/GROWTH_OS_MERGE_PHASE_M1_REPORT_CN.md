# Phase M1：宇智能主线与 Growth OS 清洁室模块能力合并报告

## 1. 测试日期

2026-07-03

## 2. 当前分支

`merge-growth-os-cleanroom`

## 3. 当前 commit 基线

合并前 tag：`before-growth-os-merge-20260703-1358`

基线 commit：`fa4bd2960ff48043c9c79f88a5fe4cff0e084314`

## 4. 源项目路径

`D:\Codex\research-imai-work-teardown`

## 5. 源项目分支和 commit

- 分支：`feature/growth-os-cleanroom`
- commit：`7df7b92192fa2fb17adf566afc12ef258ced364d`

## 6. 合并方式

采用“能力迁移 + 适配层”方式，没有复制整个项目 B。核心能力以 Python clean-room 模块重建，并接入现有制造业多 Agent 工作流与项目归档。

## 7. 未合并文件清单

- `D:\Codex\research-imai-work-teardown\.research_tmp\*`
- `D:\Codex\research-imai-work-teardown\apps\growth-os\node_modules\*`
- `D:\Codex\research-imai-work-teardown\apps\growth-os\dist\*`
- `D:\Codex\research-imai-work-teardown\apps\growth-os\build\*`
- `D:\Codex\research-imai-work-teardown\projects\growth_os_test\*`
- UI CDP 验证脚本和旧测试归档。

## 8. 被排除原因

`.research_tmp` 中包含浏览器 Profile、临时抓取输出、日志和本地研究文件，已隔离到：

`D:\OpenClaw\backups\growth-os-source-quarantine\.research_tmp-20260703-135746`

依赖、构建产物、历史测试归档和浏览器资料不进入主线仓库。

## 9. 是否发现敏感文件

发现源项目根目录下存在被忽略的 `.research_tmp` 临时研究目录，含浏览器 Profile/缓存类文件。已先隔离，隔离后重新扫描 `apps\growth-os` 模块，未发现密钥、Cookie、数据库或浏览器 Profile。

## 10. 是否发现许可证风险

未直接复制 IMAI.WORK 官方源码、接口、数据库结构、测试账号或演示数据。当前合并为 clean-room 能力重建。后续如进入商业发布，仍需保留 LobsterAI/OpenClaw 相关开源许可证声明。

## 11. Growth OS 能力映射表路径

`D:\OpenClaw\v2\growth_os\GROWTH_OS_CAPABILITY_MAP_CN.md`

## 12. 新增模块清单

- `D:\OpenClaw\v2\growth_os\action_intent`
- `D:\OpenClaw\v2\growth_os\data_acquisition`
- `D:\OpenClaw\v2\growth_os\lead_research`
- `D:\OpenClaw\v2\growth_os\content_factory`
- `D:\OpenClaw\v2\growth_os\private_domain_sop`
- `D:\OpenClaw\v2\growth_os\approval_queue`
- `D:\OpenClaw\v2\growth_os\sandbox_executor`
- `D:\OpenClaw\v2\growth_os\audit_log`
- `D:\OpenClaw\v2\growth_os\review_report`
- `D:\OpenClaw\v2\growth_os\adapters`
- `D:\OpenClaw\v2\test-cases\growth_os_merge`
- `D:\OpenClaw\v2\tests\test_growth_os_merge.py`

## 13. ActionIntent 是否实现

已实现：`D:\OpenClaw\v2\growth_os\action_intent\action_intent.py`

支持草稿、发布、评论、私信、邮件、加微信、群发、导出、删除等动作类型。真实外部动作默认 `requires_approval = true`，并标记 `disabled_by_default = true`。

## 14. Feature Flags 是否实现

已实现 example：`D:\OpenClaw\v2\config\feature_flags.example.json`

高敏感功能默认全部关闭，不提交真实 `feature_flags.json`。

## 15. Data Acquisition Layer 是否实现

已实现基础框架：`D:\OpenClaw\v2\growth_os\data_acquisition`

当前支持人工 URL、公开网页搜索结果、沙盒 CSV 的结构化建模；不接真实 API Key，不登录平台，不绕验证码。

## 16. Approval Queue 是否实现

已实现：`D:\OpenClaw\v2\growth_os\approval_queue`

工作流归档会生成：`approval_queue.json`

## 17. Sandbox Executor 是否实现

已实现：`D:\OpenClaw\v2\growth_os\sandbox_executor`

只允许本地沙盒记录草稿动作；真实外部动作返回 blocked，不会外发。

## 18. Audit Log 是否实现

已实现：`D:\OpenClaw\v2\growth_os\audit_log`

项目归档会生成：`audit_log.json`

## 19. 与 product_intelligence 联动结果

已联动。制造业工作流先调用 `product_intelligence` 生成产品画像，再传给 Growth OS adapter 生成 `product_profile.json` 和线索/内容/审批文件。

测试结果：通过。

## 20. 与 domestic_signal_growth 联动结果

已联动。`domestic_signal_growth` 的来源、商机、内容草稿、SOP 和跟进建议进入 Growth OS adapter，并转换为 ActionIntent 与审批队列。

测试结果：通过。

## 21. 与项目归档联动结果

已联动。`run_manufacturing_multi_agent_workflow.py` 在原项目归档完成后写入 Growth OS 文件：

- `product_profile.json`
- `sources.json`
- `lead_candidates.json`
- `leads.json`
- `evidence.json`
- `action_intents.json`
- `approval_queue.json`
- `sandbox_results.json`
- `audit_log.json`
- `review_report.md`

## 22. 三个工程测试用例结果

Dev Auto-Run Growth OS 合并测试：通过。

运行 ID：`phase-m1-growth-os-merge-20260703-140706`

覆盖：

- 东莞重型包装纸箱厂：通过，4 条线索，9 个 ActionIntent，1 个审批项。
- 东莞电子连接件工厂：通过，4 条线索，9 个 ActionIntent，1 个审批项。
- 东莞健身器材厂：通过，4 条线索，9 个 ActionIntent，1 个审批项。

## 23. UI 鼠标验收结果

结论：部分通过。

证据截图目录：

`D:\OpenClaw\v2\reports\assets\phase-m1-growth-os-merge-ui`

已验证：

- 通过鼠标选择 LobsterAI / 宇智能桌面 UI。
- 选择了 `宇智能制造业获客总控 Agent`。
- UI 模型显示 `DeepSeek V4 Pro`。
- 通过鼠标点击输入框、粘贴任务、点击发送。
- UI 触发了公开 Google 搜索。
- UI 生成了多 Agent 进度、文件卡片、ActionIntent 类文件和审批队列 Markdown。
- 未真实发布、评论、私信或发邮件。

未完全满足：

- UI 首轮没有调用主线 `D:\OpenClaw\v2\scripts\run_manufacturing_multi_agent_workflow.py` 归档脚本，而是在 LobsterAI AppData 工作区自由生成 Markdown 文件。
- 运行态修复后，UI 能显示总控 Agent 调度多个专业 Agent，但 200 秒内仍未返回 `D:\OpenClaw\v2\projects` 主线归档路径。
- 因此不能写结论 A。

已做修复：

- 更新 `dev-autorun-gate.py` 的总控 Agent prompt，要求 Growth OS / ActionIntent / 审批队列任务必须优先调用制造业工作流 Skill。
- 更新 `manufacturing_multi_agent_workflow` Skill 文档和 manifest，显式声明 `action_intents.json`、`approval_queue.json`、`review_report.md` 输出。
- 本机 LobsterAI SQLite 中已临时把总控 Agent 绑定到 `manufacturing_multi_agent_workflow`，用于复测。

## 24. 是否保持 draft_only

是。工程工作流和 UI 验收均未执行真实外部动作。

## 25. 是否有真实外发

否。未真实发布、评论、私信、发邮件、加微信或群发。

## 26. 是否仍依赖 fallback

工程路径不依赖 fallback，能由本地工作流脚本生成标准归档。

UI 路径仍部分依赖 LobsterAI/Cowork 自由执行行为，尚未稳定强制进入主线工作流脚本，所以 UI 结论为部分通过。

## 27. 是否建议进入 Phase 3A：真实数据源接入

不建议直接进入完整 Phase 3A。建议先做 Phase M1.1：LobsterAI UI 到主线制造业工作流 Skill 的强绑定修复。

## 28. 下一步建议

1. Phase M1.1：让总控 Agent 在 UI 中点击发送后，必须调用 `manufacturing_multi_agent_workflow`，并直接返回 `D:\OpenClaw\v2\projects` 项目路径。
2. 在 LobsterAI UI 中减少可自由选择错误 Skill 的机会，把制造业总控 Agent 的默认 Skill 固定为 `manufacturing_multi_agent_workflow`。
3. 把 UI 生成的 AppData Markdown 临时项目迁移/映射到主线项目归档，避免用户看到两个成果位置。
4. 修复 UI 任务状态长时间停留“运行中”的问题。
5. M1.1 通过后再进入 Phase 3A：真实数据源接入。

## 工程测试命令结果

- `python -m py_compile D:\OpenClaw\v2\growth_os\action_intent\action_intent.py`：通过。
- `python -m py_compile D:\OpenClaw\v2\growth_os\data_acquisition\data_source_registry.py`：通过。
- `python -m unittest D:\OpenClaw\v2\tests\test_growth_os_merge.py -v`：4/4 通过。
- `python -m unittest discover D:\OpenClaw\v2\skills\product_intelligence\tests -v`：3/3 通过。
- `python -m unittest discover D:\OpenClaw\v2\skills\domestic_signal_growth\tests -v`：6/6 通过。
- `python -m unittest discover D:\OpenClaw\v2\tests -v`：10/10 通过。
- `python D:\OpenClaw\v2\scripts\dev-autorun-gate.py --run-growth-os-merge`：通过。

## 结论

B. 部分成立，先修复 Growth OS 与宇智能 UI 联动问题。

工程合并已经成立，但 UI 鼠标验收没有稳定返回主线归档路径，不能进入 Phase 3A。
