# Growth OS 能力映射表

| Growth OS 能力 | 合并到宇智能位置 | 当前状态 | 是否可用 | 是否高敏感 | 默认开关 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| Project Workspace | `D:\OpenClaw\v2\projects` | 已接入现有项目归档 | 是 | 否 | 开启 | 工作流结果仍写入原项目工作区。 |
| Real Data Acquisition Layer | `D:\OpenClaw\v2\growth_os\data_acquisition` | 已实现基础框架 | 是 | 中 | `draft_only` | 只支持人工 URL、公开来源、沙盒 CSV 框架，不接真实 API Key。 |
| Lead Research Agent | `D:\OpenClaw\v2\growth_os\lead_research`，并与 `domestic_signal_growth` 联动 | 已实现 MVP | 是 | 中 | `draft_only` | 没来源的线索标记 unverified，不直接触达。 |
| Content Factory Agent | `D:\OpenClaw\v2\growth_os\content_factory` | 已实现 MVP | 是 | 低 | 开启 | 只生成内容草稿。 |
| Private Domain SOP Agent | `D:\OpenClaw\v2\growth_os\private_domain_sop` | 已实现 MVP | 是 | 高 | `draft_only` | 只生成 SOP、评论草稿、私信草稿，不真实私信/加微/群发。 |
| ActionIntent | `D:\OpenClaw\v2\growth_os\action_intent` | 已实现 | 是 | 高 | `draft_only` | 所有潜在外部动作统一建模。 |
| Risk Control / Feature Flags | `D:\OpenClaw\v2\config\feature_flags.example.json`、`D:\OpenClaw\v2\growth_os\approval_queue` | 已实现 example 和队列 | 是 | 高 | 全部关闭 | 只提交 example，不提交真实 `feature_flags.json`。 |
| Sandbox Executor | `D:\OpenClaw\v2\growth_os\sandbox_executor` | 已实现 | 是 | 中 | 本地沙盒 | 只记录草稿动作；真实外部动作返回 blocked。 |
| Approval Queue | `D:\OpenClaw\v2\growth_os\approval_queue` | 已实现 | 是 | 高 | pending | 通过/驳回只是本地状态，后续 UI 再接。 |
| Audit Log | `D:\OpenClaw\v2\growth_os\audit_log` | 已实现 | 是 | 中 | 开启 | 记录本地意图、沙盒检查、归档动作。 |
| Review Report | `D:\OpenClaw\v2\growth_os\review_report` | 已实现 | 是 | 否 | 开启 | 输出 `review_report.md` 到项目归档目录。 |

## 高敏感默认策略

- 真实发布、评论、私信、邮件、加微信、群发、批量导出默认关闭。
- 所有外部动作必须先进入 ActionIntent 和审批队列。
- Phase M1 不连接真实社媒账号，不读取 secrets，不绕过验证码。
