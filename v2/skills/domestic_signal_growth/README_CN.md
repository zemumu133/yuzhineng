# domestic_signal_growth MVP

`domestic_signal_growth` 是“宇智能”的国内获客信号 Skill。它负责把一个产品推广目标拆成公开来源、商机判断、目标客户类型、内容建议、跟进草稿、人工待办和风险提示。

## 当前能力

- 输入产品、行业、目标客户、平台和区域。
- 通过 `search_adapter.py` 尝试使用 LobsterAI web-search bridge 获取公开来源。
- 当 web-search 连接失效时自动重新 `launch/connect`。
- 没有真实来源时返回 `source_status=unverified` 或 `search_failed`，不会伪造 URL。
- 输出全程 `draft_only`，不真实发布、不评论、不私信、不发邮件。

## PowerShell 调用

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\v2\skills\domestic_signal_growth\domestic_signal_growth.ps1" -InputFile "D:\OpenClaw\v2\skills\domestic_signal_growth\examples\certificate_training.json"
```

旧入口 `hello_growth.ps1` 已保留，会转发到新入口。

## 输入格式

```json
{
  "product": "职业证书考评服务",
  "industry": "教育培训",
  "target_customers": ["培训机构", "人力资源公司"],
  "city": "全国",
  "platforms": ["小红书", "抖音"],
  "mode": "draft_only",
  "search_required": true
}
```

## 输出重点

- `source_status`：`verified_public_sources`、`unverified` 或 `search_failed`。
- `sources`：公开来源数组，必须来自真实 URL。
- `opportunity_judgement`：商机判断。
- `target_customer_types`：客户类型、痛点、购买信号、决策人。
- `platform_strategy`：小红书、抖音、公众号内容策略。
- `followup_drafts`：评论/私信等草稿，不自动发送。
- `todos`：人工审批和下一步待办。

## 安全边界

本 Skill 不读取 secrets，不调用真实社媒账号，不发送任何外部动作，不采集私人联系方式，不绕过验证码、登录墙或平台限制。
