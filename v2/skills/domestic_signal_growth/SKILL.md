# domestic_signal_growth

## Purpose

Domestic marketing signal analysis for "宇智能" growth workflows.

Use this skill when the user wants to evaluate a Chinese-market growth,
lead-generation, content-marketing, or social-operation task for a product or
service. It is designed for draft-only business planning.

## Safety Boundary

- Do not send email.
- Do not send direct messages.
- Do not post content.
- Do not comment on social platforms.
- Do not log into social accounts.
- Do not collect private contact data.
- Do not invent public sources, contacts, phone numbers, WeChat IDs, or emails.
- Treat every external action as `draft_only` unless the user explicitly handles it outside the app.

## Local Command

Run the local helper script with PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\v2\skills\domestic_signal_growth\hello_growth.ps1" -InputJson '{"product":"职业证书考评服务","target_customers":["培训机构","人力资源公司"],"platforms":["小红书","抖音"],"mode":"draft_only"}'
```

## Expected Input

```json
{
  "product": "职业证书考评服务",
  "target_customers": ["培训机构", "人力资源公司"],
  "platforms": ["小红书", "抖音"],
  "mode": "draft_only"
}
```

## Expected Output

The command returns JSON with these fields:

- `opportunity_judgement`
- `target_customer_types`
- `xiaohongshu_content_ideas`
- `douyin_content_ideas`
- `followup_drafts`
- `todos`
- `risk_notes`

Summarize the JSON for the user in Chinese. Keep raw JSON in advanced details
only when the user asks for it.
