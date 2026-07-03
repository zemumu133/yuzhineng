# Phase M1.1：UI 数据分层、Agent 去重、Growth OS 主线归档路径修复报告

## 1. 测试日期

2026-07-03 15:04 +08:00

## 2. 当前分支与基线

- 当前分支：`merge-growth-os-cleanroom`
- Phase M1 基线 commit：`949ccbdb1f909a1d33ec7d5bc84b0c2ff780cab4`

## 3. 修改文件清单

- `.gitignore`
- `v2/AGENT_TAXONOMY_CN.md`
- `v2/GITHUB_RELEASE_PREP_CN.md`
- `v2/config/agent_taxonomy.json`
- `v2/growth_os/adapters/manufacturing_growth_adapter.py`
- `v2/scripts/archive_manufacturing_growth_result.py`
- `v2/scripts/real_agent_collaboration.py`
- `v2/scripts/repair_lobsterai_agent_taxonomy.py`
- `v2/scripts/repair_lobsterai_agent_taxonomy.ps1`
- `v2/tests/test_agent_taxonomy_and_sidebar.py`
- `v2/tests/test_growth_os_archive_path.py`
- `v2/workflows/dongguan_manufacturing_growth/multi_agent_workflow.json`

## 4. Agent 分类标准

已完成。新增 `v2/AGENT_TAXONOMY_CN.md` 和 `v2/config/agent_taxonomy.json`，标准化 9 个宇智能 Agent：

1. 宇智能制造业获客总控 Agent
2. 产品理解 Agent
3. 商机发掘 Agent
4. 宣传物料 Agent
5. 社媒运营 Agent
6. 工厂对接 Agent
7. 风控审核 Agent
8. 归纳 Agent
9. 归档 Agent

## 5. Agent 去重映射

已完成。

- `yuzhineng-lead-agent` / 宇智能获客 Agent -> `yuzhineng-opportunity-researcher`
- `yuzhineng-content-agent` / 宇智能内容 Agent -> `yuzhineng-content-producer`
- `yuzhineng-sales-agent` / 宇智能销售 Agent -> `yuzhineng-factory-handoff`
- `yuzhineng-marketing-agent` / 宇智能营销 Agent -> 宣传物料 Agent + 社媒运营 Agent 职责拆分

真实 LobsterAI SQLite 修复结果：

- 标准 Agent：9 个
- 可见标准 Agent：9 个
- 仍启用的废弃 Agent：0 个
- 本次禁用废弃 Agent：3 个
- SQLite 备份：`D:\OpenClaw\backups\lobsterai-sqlite\lobsterai-before-m1-1-agent-taxonomy-20260703-144700.sqlite`

## 6. UI 左侧 Agent 列表修复方式

根因：

- 历史阶段创建了多个职责相近的自定义 Agent。
- Electron 前端会按 `agents.enabled` 过滤，但正在运行的 renderer 有旧内存状态，需要重启 Electron 才能重新加载 SQLite。
- 旧会话继续执行时可能使用旧 active skills，不能代表新任务的默认行为。

修复：

- 新增 `repair_lobsterai_agent_taxonomy.py`，可重复修复 LobsterAI SQLite。
- 标准 Agent 不存在则创建，存在则更新名称、职责、模型、技能和工作目录。
- 废弃 Agent 不物理删除，只禁用并保留历史。
- 成果文件类历史会话会写入 `yuzhineng_ui_items`，类型为 `file`，显示区域为 `project_workspace`，避免后续把文件当成 Agent。
- 新任务默认总控 Agent 包含 `manufacturing_multi_agent_workflow`，不再退回单一 `domestic_signal_growth`。

## 7. 文件混入 Agent 列表

已修复数据来源层：

- 新增 `item_type`
- 新增 `owner_agent_id`
- 新增 `project_id`
- 新增 `file_type`
- 新增 `display_area`

Growth OS 项目会生成 `ui_delivery_items.json`，文件、报告、交接单、审批队列、ActionIntent 都进入 `project_workspace` 或 `file_panel`，不进入 `sidebar`。

## 8. Growth OS 主线归档路径

已修复。

- 主线项目根目录：`D:\OpenClaw\v2\projects`
- 兼容入口：`D:\OpenClaw\v2\projects\index.html`
- 主线入口：`D:\OpenClaw\v2\projects\projects_index.html`

最新 UI 鼠标验收项目：

`D:\OpenClaw\v2\projects\20260703-080156-重型包装纸箱厂-重型包装纸箱-物流包装-出口包装-multi-agent`

必需文件已全部存在：

- `input.json`
- `project_manifest.json`
- `sources.json`
- `evidence.json`
- `lead_candidates.json`
- `leads.json`
- `action_intents.json`
- `approval_queue.json`
- `report.md`
- `handoff.docx`
- `safety_check.json`
- `review_report.md`
- `README_CN.md`
- `ui_delivery_items.json`

## 9. ActionIntent 与审批队列

- `action_intents.json`：9 条
- `approval_queue.json`：1 条
- 审批状态：`pending`
- 动作模式：`draft_only`
- `real_external_send`：`false`

## 10. projects_index.html

已显示新项目，并提供按钮/链接：

- 总报告
- 产品资料卡
- 线索/商机
- ActionIntent
- 审批队列
- 工厂交接单
- 风控复核
- Agent 工作群
- 成果工作台

## 11. GitHub 发布准备

- 文档：`D:\OpenClaw\v2\GITHUB_RELEASE_PREP_CN.md`
- 已添加 remote：`github-yuzhineng`
- remote URL：`https://github.com/zemumu133/yuzhineng.git`
- 本阶段未 push。

## 12. LobsterAI Patch

本阶段没有修改 `D:\OpenClaw\v2\client-shell\lobsterai\src` 下的上游源码，因此没有导出 LobsterAI patch。

修复采用：

- 主线可提交脚本
- 运行时 SQLite taxonomy 修复
- Growth OS 适配层数据分层
- 主线工作流配置修复

## 13. UI 鼠标验收

验收路径：

- 截图目录：`D:\OpenClaw\v2\reports\assets\phase-m1-1-ui-agent-dedup-archive\`
- UI 轨迹：`D:\OpenClaw\v2\data\ui-runs\phase-m1-1-ui-agent-dedup-archive\ui-validation-result.json`

过程说明：

1. 真实打开 LobsterAI Electron 桌面 UI。
2. 重启 Electron，使其重新读取修复后的 SQLite。
3. 选择“宇智能制造业获客总控 Agent”。
4. 确认新任务输入框上方出现 `manufacturing_multi_agent_workflow` 和 `domestic_signal_growth`。
5. 确认模型为 DeepSeek V4 Pro。
6. 用鼠标点击输入框、粘贴任务、点击发送。
7. UI 返回 `projects_index.html`、`handoff.docx`、`agent_group_chat.html`、`agent_workspace.html` 等主线成果入口。
8. UI 显示 9 个 Agent 协作完成，零真实外发。

注意：第一次在旧会话中继续任务时，UI 没有稳定触发主线 Growth OS 归档；因此本阶段明确结论以“新建任务 + 修复后默认技能”的验收结果为准。

## 14. 工程测试结果

已通过：

- `python -m unittest D:\OpenClaw\v2\tests\test_agent_taxonomy_and_sidebar.py -v`
- `python -m unittest D:\OpenClaw\v2\tests\test_growth_os_archive_path.py -v`
- `python -m unittest D:\OpenClaw\v2\tests\test_growth_os_merge.py -v`
- `python -m unittest discover D:\OpenClaw\v2\tests -v`
- `python -m unittest discover D:\OpenClaw\v2\skills\product_intelligence\tests -v`
- `python -m unittest discover D:\OpenClaw\v2\skills\domestic_signal_growth\tests -v`
- `python D:\OpenClaw\v2\scripts\dev-autorun-gate.py --run-growth-os-merge`

Dev Auto-Run Growth OS 测试结果：

- 3 个样例均 `ok=true`
- 每个样例均生成 ActionIntent、审批队列、review_report、report、handoff
- `real_external_send=false`

## 15. 安全检查

- 未读取 secrets。
- 未提交 API Key / Token / Cookie / 浏览器 Profile。
- 未真实发布。
- 未真实评论。
- 未真实私信。
- 未真实发邮件。
- 未登录社媒账号。
- 未推送 GitHub。
- 本次 UI 项目所有外部动作保持 `draft_only` 或 `approval_required`。

## 16. 已知限制

1. 旧会话可能仍带旧 active skills；建议用户从“新建任务”启动 Growth OS 工作流。
2. LobsterAI 自带主 Agent / 产品经理没有被禁用，避免误伤通用功能；本阶段只清理宇智能重复 Agent。
3. 项目成果中心当前仍以本地 HTML 文件为最小入口，后续可在 LobsterAI 内置页面中做更正式的成果中心。
4. UI 鼠标验收中桌面窗口焦点竞争明显，后续打包版需要减少 DevTools/浏览器干扰。

## 17. 结论

A. UI 数据分层、Agent 去重和 Growth OS 主线归档路径修复完成，允许进入 PACK-1：可移植安装包 PoC。

满足条件：

- 工程测试通过。
- UI 鼠标验收通过。
- 左侧标准宇智能 Agent 不重复。
- 新任务稳定使用 `manufacturing_multi_agent_workflow`。
- Growth OS UI 任务返回 `D:\OpenClaw\v2\projects` 项目归档路径。
- 项目归档包含 `action_intents.json` 和 `approval_queue.json`。
- `projects_index.html` 能打开新项目。
- 高敏感动作保持 `draft_only` / `approval_required`。
- 无真实外发。
- 未依赖 fallback 冒充成功。

## 18. 下一步建议

进入 PACK-1：可移植安装包 PoC。重点验证：

1. 新设备恢复 Agent taxonomy。
2. 新设备启动 LobsterAI 后默认进入宇智能总控 Agent。
3. `projects_index.html` 或内置成果中心可被普通用户找到。
4. 打包版不暴露开发 DevTools、不提交运行数据。
