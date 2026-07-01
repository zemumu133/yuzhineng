# Phase 1A-DevAutoRunGate：开发测试自动权限与多 Agent 任务验证

## 1. 测试日期

- 测试时间：2026-07-01 18:19:19 +0800
- Run ID：20260701-181919

## 2. 当前 LobsterAI commit

- 当前工作区基线来自上一阶段 commit：5348d6a9a75b002a95e1545fd5ca1571f03eb16b
- 本阶段未提交 LobsterAI 上游源码目录，避免把 PoC 外部源码纳入 v2 基线。

## 3. Dev Auto-Run 是否实现

- 已实现本地开发测试通道：`v2/scripts/dev-autorun-gate.py` 与 `v2/scripts/dev-autorun-gate.ps1`。
- 默认关闭；只有 `YUZHINENG_DEV_AUTO_RUN=1` 且本地 `v2/dev-config/dev-auto-run.json` 中 `enabled=true` 时运行。
- 真实本地配置 `dev-auto-run.json` 已加入 `.gitignore`，仓库只提交 `.example`。

## 4. 是否有 UI 审批入口

- 本阶段未实现正式 UI 审批入口。
- 继续保留上一阶段判断：Cowork 普通 UI 仍缺少 `operator.admin/operator.write` scope upgrade 的可见批准入口。

## 5. allowed_scopes

```json
[
  "cowork.session.create",
  "cowork.session.send",
  "agent.test.create",
  "agent.test.update",
  "agent.test.delete",
  "task.test.create",
  "task.test.update",
  "skill.domestic_signal_growth.call",
  "tool.web_search.public",
  "tool.document.local",
  "write.v2.reports",
  "write.v2.data.test_runs",
  "read.v2.docs",
  "read.v2.skills"
]
```

## 6. denied_scopes

```json
[
  "read.secrets",
  "read.api_keys",
  "read.tokens",
  "read.cookies",
  "read.browser_profiles",
  "social.login",
  "email.send",
  "dm.send",
  "comment.post",
  "post.publish",
  "official.bundle.install",
  "official.update.download",
  "payment.call",
  "ads.call",
  "customer_data.bulk_export",
  "system.path.modify",
  "system.install.large",
  "legacy_console.modify",
  "operator.admin.global_allow"
]
```

## 7. 是否默认关闭

- 是。example 中 `enabled=false`，脚本还要求环境变量 `YUZHINENG_DEV_AUTO_RUN=1`。

## 8. 如何开启

```powershell
D:\OpenClaw\v2\scripts\dev-autorun-gate.ps1 -InitLocalConfig
D:\OpenClaw\v2\scripts\dev-autorun-gate.ps1 -Run
```

## 9. 如何关闭

- 删除或禁用 `D:\OpenClaw\v2\dev-config\dev-auto-run.json`。
- 取消环境变量 `YUZHINENG_DEV_AUTO_RUN`。

## 10. 是否使用 deepseek/deepseek-v4-pro

- 三轮任务实际模型均为 V4 Pro：True

## 11. 三个测试 Agent 创建结果

```json
[
  {
    "agent_id": "yuzhineng-lead-agent",
    "name": "宇智能获客 Agent",
    "openclaw_created": false,
    "openclaw_already_existed": true,
    "openclaw_add_code": null,
    "identity_code": 0,
    "workspace": "D:\\OpenClaw\\v2\\data\\test-runs\\workspaces\\yuzhineng-lead-agent",
    "agent_dir": "D:\\OpenClaw\\v2\\data\\test-runs\\openclaw-agents\\yuzhineng-lead-agent"
  },
  {
    "agent_id": "yuzhineng-content-agent",
    "name": "宇智能内容 Agent",
    "openclaw_created": false,
    "openclaw_already_existed": true,
    "openclaw_add_code": null,
    "identity_code": 0,
    "workspace": "D:\\OpenClaw\\v2\\data\\test-runs\\workspaces\\yuzhineng-content-agent",
    "agent_dir": "D:\\OpenClaw\\v2\\data\\test-runs\\openclaw-agents\\yuzhineng-content-agent"
  },
  {
    "agent_id": "yuzhineng-sales-agent",
    "name": "宇智能销售 Agent",
    "openclaw_created": false,
    "openclaw_already_existed": true,
    "openclaw_add_code": null,
    "identity_code": 0,
    "workspace": "D:\\OpenClaw\\v2\\data\\test-runs\\workspaces\\yuzhineng-sales-agent",
    "agent_dir": "D:\\OpenClaw\\v2\\data\\test-runs\\openclaw-agents\\yuzhineng-sales-agent"
  }
]
```

## 12. LobsterAI UI Agent 镜像结果

```json
[
  {
    "agent_id": "yuzhineng-lead-agent",
    "name": "宇智能获客 Agent",
    "lobsterai_ui_mirrored": true,
    "previous_row_existed": true
  },
  {
    "agent_id": "yuzhineng-content-agent",
    "name": "宇智能内容 Agent",
    "lobsterai_ui_mirrored": true,
    "previous_row_existed": true
  },
  {
    "agent_id": "yuzhineng-sales-agent",
    "name": "宇智能销售 Agent",
    "lobsterai_ui_mirrored": true,
    "previous_row_existed": true
  }
]
```

## 13. 三个测试任务创建结果

### task-001-certificate

- 完成：True
- OpenClaw session：5b41fea7-9237-4000-994f-90d9782858df
- LobsterAI UI session：{'ok': True, 'session_id': 'dev-autorun-20260701-181919-task-001-certificate'}
- 摘要：职业证书考评服务 对 培训机构、人力资源公司 有明确的内容获客机会，适合先用公开信息研究、痛点内容和人工审批触达验证需求。
- 质量提醒：web-search 已触发但 provider 不可用，本轮没有真实公开来源。

### task-002-carton

- 完成：True
- OpenClaw session：31a22628-fa23-4d3f-b6a1-bd23ce21fac1
- LobsterAI UI session：{'ok': True, 'session_id': 'dev-autorun-20260701-181919-task-002-carton'}
- 摘要：web_search 不可用，按规则输出。注意：domestic_signal_growth 返回的内容与"重型包装纸箱"主题存在偏差（结果偏向职业证书领域），已如实保留原始数据并在输出中标注。
- 质量提醒：结构化 JSON 未成功解析，已保留原始轨迹，后续需强化 JSON 输出约束。；web-search 已触发但 provider 不可用，本轮没有真实公开来源。

### task-003-fitness

- 完成：True
- OpenClaw session：bee7a7a5-73f1-445d-9391-893fb9426cbd
- LobsterAI UI session：{'ok': True, 'session_id': 'dev-autorun-20260701-181919-task-003-fitness'}
- 摘要：健身器材外贸/内贸产品 对 健身房、经销商、跨境卖家 有明确的内容获客机会，适合先用公开信息研究、痛点内容和人工审批触达验证需求。
- 质量提醒：web-search 已触发但 provider 不可用，本轮没有真实公开来源。

## 14. web-search 调用结果

- 是否触发：True
- 失败数合计：3
- 说明：本轮 OpenClaw agent 能触发 `web_search` 工具，但当前 provider 未配置或不可用时，模型会返回失败状态并继续生成 draft_only 结果。

## 15. domestic_signal_growth 调用结果

- 三轮本地 Skill 均已调用：True

## 16. 最小业务结果摘要

- task-001-certificate：职业证书考评服务 对 培训机构、人力资源公司 有明确的内容获客机会，适合先用公开信息研究、痛点内容和人工审批触达验证需求。
  质量提醒：web-search 已触发但 provider 不可用，本轮没有真实公开来源。
- task-002-carton：web_search 不可用，按规则输出。注意：domestic_signal_growth 返回的内容与"重型包装纸箱"主题存在偏差（结果偏向职业证书领域），已如实保留原始数据并在输出中标注。
  质量提醒：结构化 JSON 未成功解析，已保留原始轨迹，后续需强化 JSON 输出约束。；web-search 已触发但 provider 不可用，本轮没有真实公开来源。
- task-003-fitness：健身器材外贸/内贸产品 对 健身房、经销商、跨境卖家 有明确的内容获客机会，适合先用公开信息研究、痛点内容和人工审批触达验证需求。
  质量提醒：web-search 已触发但 provider 不可用，本轮没有真实公开来源。

## 17. 安全检查结果

- 未读取 `D:\OpenClaw\secrets`。
- 未提交 API Key、Token、Cookie、浏览器 Profile。
- 未真实发送邮件、私信、评论或发帖。
- 未登录社媒账号。
- 未下载官方更新包。
- 未全局关闭权限检查。
- Dev Auto-Run 仅由本地环境变量和本地配置显式开启。

## 18. 是否建议进入 Phase 2

- 结论：B：部分成立，先修复具体阻塞点
- 建议：先修复 web-search provider 配置和 Cowork UI scope approval，再进入完整 Phase 2。

## 19. 下一步建议

1. 给 Cowork 的 `operator.admin/operator.write` scope upgrade 增加可见审批入口，或把开发测试 runner 与普通 UI runner 分离。
2. 配置 OpenClaw web_search provider，使公开搜索不再失败。
3. 把 `domestic_signal_growth` 从占位 PowerShell Skill 升级为可被 Cowork/OpenClaw 原生发现的 Skill 或 MCP 工具。
4. 修复 UI 会话模型默认值，深度任务默认使用 `deepseek/deepseek-v4-pro`。

## 20. 回滚方式

- 删除 `D:\OpenClaw\v2\dev-config\dev-auto-run.json`。
- 删除 `D:\OpenClaw\v2\data\test-runs\` 下本轮测试目录。
- 在 LobsterAI UI 中删除 ID 前缀为 `yuzhineng-` 的测试 Agent/会话，或使用后续清理脚本。
- 回退本阶段 Git commit。
