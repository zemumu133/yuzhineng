# manufacturing_multi_agent_workflow

## Purpose

Use this Skill when the user asks "宇智能获客总控 Agent" to start a
manufacturing growth workflow. It is a controlled local orchestrator, not a
free-form command runner.

## Safety Boundary

- Keep every external action as `draft_only`.
- Do not send email.
- Do not send private messages.
- Do not post comments.
- Do not publish social posts.
- Do not log into social accounts.
- Do not read secrets.
- Do not invent public sources, contacts, phone numbers, WeChat IDs, or emails.

## Local Command

Run the local helper script with PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\v2\skills\manufacturing_multi_agent_workflow\run_manufacturing_multi_agent_workflow.ps1" -InputJson '{"company_location":"东莞","factory_type":"电子配件厂","product_name":"电子连接件、线束、充电配件","target_customer_hint":["电子厂","品牌商","跨境卖家"],"platforms":["小红书","抖音","公众号"],"mode":"draft_only"}'
```

## Expected Output

The command returns JSON containing:

- `workflow_run_dir`
- `project_dir`
- `report_path`
- `handoff_path`
- `projects_index_html`
- `agent_count`
- `safety`

After the command succeeds, summarize the generated `report.md` in Chinese.
The user should see:

- 总控 Agent 任务拆解
- 产品理解 Agent 输出
- 商机发掘 Agent 输出
- 宣传物料 Agent 输出
- 社媒运营 Agent 输出
- 工厂对接 Agent 输出
- 风控审核 Agent 输出
- 归档 Agent 输出

Keep raw JSON in advanced details only when the user asks for it.
