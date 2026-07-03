# 宇智能 Agent 命名规范与去重规则

## 目标

宇智能只保留一套清晰、唯一、可维护的制造业获客 Agent 体系。Agent 列表只显示标准 Agent 和它们下属的任务/会话预览；报告、交接单、JSON、Markdown 等成果文件必须进入项目成果中心、项目工作区或 Agent 详情文件区，不再伪装成 Agent 或任务。

## 标准 Agent

| Agent ID | 中文名 | 职责边界 | 默认技能 |
| --- | --- | --- | --- |
| `yuzhineng-manufacturing-chief` | 宇智能制造业获客总控 Agent | 接收用户总任务，拆解任务，调度专业 Agent，汇总状态，触发归纳和归档。 | `manufacturing_multi_agent_workflow`, `product_intelligence`, `domestic_signal_growth`, `web-search`, `archive_manufacturing_growth_result` |
| `yuzhineng-product-analyst` | 产品理解 Agent | 理解产品资料，生成产品画像、产品资料卡、卖点、适合客户和缺失信息。 | `product_intelligence` |
| `yuzhineng-opportunity-researcher` | 商机发掘 Agent | 整理公开来源、目标客户、采购信号、线索候选、evidence 和商机评分。 | `domestic_signal_growth`, `web-search` |
| `yuzhineng-content-producer` | 宣传物料 Agent | 生成小红书笔记、抖音脚本、公众号大纲、产品介绍和销售话术草稿。 | `domestic_signal_growth` |
| `yuzhineng-social-operator` | 社媒运营 Agent | 生成 7 天发布计划、评论回复草稿、私信草稿和账号养成计划；不真实发布、评论或私信。 | `domestic_signal_growth` |
| `yuzhineng-factory-handoff` | 工厂对接 Agent | 生成工厂销售客户交接单、跟进 SOP、销售待办和 `handoff.docx`。 | `domestic_signal_growth`, `docx` |
| `yuzhineng-safety-reviewer` | 风控审核 Agent | 检查真实外发、夸大宣传、来源伪造、敏感信息和 `draft_only` 声明。 | 无默认外部工具 |
| `yuzhineng-summary-agent` | 归纳 Agent | 读取各 Agent 输出、返工日志和项目文件，生成最终总结、缺失项和下一步建议。 | `manufacturing_multi_agent_workflow` |
| `yuzhineng-archive-agent` | 归档 Agent | 保存项目成果并更新 `project_manifest.json`、`projects_index.json`、`index.html`。 | `archive_manufacturing_growth_result` |

## 合并与废弃映射

| 废弃名称 | 废弃 ID | 合并到 | 规则 |
| --- | --- | --- | --- |
| 宇智能获客 Agent | `yuzhineng-lead-agent` | 商机发掘 Agent | 线索、商机、公开研究统一归口。 |
| 宇智能内容 Agent | `yuzhineng-content-agent` | 宣传物料 Agent | 内容生成统一归口。 |
| 宇智能销售 Agent | `yuzhineng-sales-agent` | 工厂对接 Agent | 销售交接、SOP、待办统一归口。 |
| 宇智能营销 Agent | `yuzhineng-marketing-agent` | 宣传物料 Agent / 社媒运营 Agent | 内容生产归宣传物料，发布计划和互动草稿归社媒运营。 |

## UI 数据分层规则

| item_type | 显示区域 | 说明 |
| --- | --- | --- |
| `agent` | `sidebar` | 只允许标准 Agent 出现在左侧 Agent 列表。 |
| `task` | `sidebar` | Agent 下属任务/会话预览可显示在 Agent 下。 |
| `conversation` | `sidebar` | 用户与某 Agent 的对话可显示在 Agent 下。 |
| `file` | `project_workspace` 或 `file_panel` | `.md`、`.docx`、`.json`、`.html` 等成果文件不进入 Agent 列表。 |
| `project` | `project_workspace` | 项目目录和项目索引入口。 |
| `report` | `project_workspace` 或 `file_panel` | `report.md`、`review_report.md` 等报告文件。 |
| `handoff_document` | `project_workspace` 或 `file_panel` | `handoff.docx`。 |
| `approval` | `project_workspace` | 审批队列。 |
| `action_intent` | `project_workspace` | ActionIntent 草稿动作。 |

## 迁移规则

1. 标准 Agent 如果不存在，则创建；如果存在，则更新名称、职责、模型、技能和工作目录。
2. 废弃 Agent 不物理删除，避免破坏历史数据；它们会被禁用，历史会话迁移到目标标准 Agent。
3. 已被误写成会话的成果文件会生成 `item_type=file` 的分类记录，并移出可见 Agent 侧边栏。
4. 所有 Growth OS 项目成果必须写入 `D:\OpenClaw\v2\projects`，并在项目目录中保留 `ui_delivery_items.json` 作为前端展示适配层。
5. 所有外部动作保持 `draft_only` 或 `approval_required`，不自动发布、评论、私信或发邮件。

## UI 显示规则

1. 左侧 Agent 列表只显示标准 Agent，每个标准 Agent 只出现一次。
2. 成果文件统一进入项目成果中心、项目工作区、Agent 详情文件区或 `projects_index.html`。
3. 普通用户不需要理解数据库表名或 JSON 字段；前端应优先展示中文摘要和清晰按钮。
4. 如果需要保留历史兼容项，默认隐藏在侧边栏之外，不影响标准 Agent 列表。
