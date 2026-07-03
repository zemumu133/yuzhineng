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
- `growth_os.files.action_intents`
- `growth_os.files.approval_queue`
- `growth_os.files.review_report`
- `growth_os.files.lead_candidates`
- `growth_os.files.evidence`
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
- 归纳 Agent 最终总结
- 归档 Agent 输出
- Agent 工作群入口：`agent_group_chat.html`
- Agent 成果工作台入口：`agent_workspace.html`
- Growth OS 文件：`action_intents.json`
- Growth OS 文件：`approval_queue.json`
- Growth OS 文件：`review_report.md`

Keep raw JSON in advanced details only when the user asks for it.

Do not create a separate Markdown-only project by hand when this Skill is
available. The source of truth is the local workflow script output and the
`D:\OpenClaw\v2\projects` archive it returns.

## Phase 2F UI Mirroring

The PowerShell wrapper enables `MirrorLobsterAIUI` by default. It writes local
draft-only cowork sessions for each professional Agent so the LobsterAI left
sidebar can show task entries under those Agents. The script backs up the local
SQLite database before writing. Disable this only for tests:

```powershell
-MirrorLobsterAIUI:$false
```
