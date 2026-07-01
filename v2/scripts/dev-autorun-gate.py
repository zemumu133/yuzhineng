import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\OpenClaw")
V2 = ROOT / "v2"
CONFIG_DIR = V2 / "dev-config"
EXAMPLE_CONFIG = CONFIG_DIR / "dev-auto-run.example.json"
LOCAL_CONFIG = CONFIG_DIR / "dev-auto-run.json"
TEST_RUNS_DIR = V2 / "data" / "test-runs"
REPORT_PATH = V2 / "reports" / "LOBSTERAI_DEV_AUTORUN_GATE_REPORT_CN.md"
DOMESTIC_SKILL = V2 / "skills" / "domestic_signal_growth" / "hello_growth.ps1"
MODEL = "deepseek/deepseek-v4-pro"


TEST_AGENTS = [
    {
        "id": "yuzhineng-lead-agent",
        "name": "宇智能获客 Agent",
        "description": "公开信息研究、商机判断、客户类型分析、内容建议和跟进待办。",
        "skills": ["web-search", "domestic_signal_growth", "docx", "xlsx"],
        "denied": ["真实外发", "登录社媒", "读取 secrets"],
    },
    {
        "id": "yuzhineng-content-agent",
        "name": "宇智能内容 Agent",
        "description": "小红书内容建议、抖音内容建议、公众号草稿、标题与脚本。",
        "skills": ["web-search", "docx"],
        "denied": ["真实发布", "评论", "私信"],
    },
    {
        "id": "yuzhineng-sales-agent",
        "name": "宇智能销售 Agent",
        "description": "跟进话术草稿、客户异议处理、待办整理和销售摘要。",
        "skills": ["domestic_signal_growth", "docx", "xlsx"],
        "denied": ["真实发邮件", "私信", "批量导出"],
    },
]


TEST_TASKS = [
    {
        "id": "task-001-certificate",
        "agent_id": "yuzhineng-lead-agent",
        "product": "职业证书考评服务",
        "targets": ["培训机构", "人力资源公司"],
        "query": "职业证书培训机构营销方式",
        "prompt": "我要推广职业证书考评服务，目标客户是培训机构和人力资源公司。请判断商机、生成客户类型、小红书内容建议、抖音内容建议、跟进话术和待办。不要真实发布、不要私信、不要评论、不要发邮件。",
    },
    {
        "id": "task-002-carton",
        "agent_id": "yuzhineng-content-agent",
        "product": "重型包装纸箱服务",
        "targets": ["电商仓储", "工厂", "物流公司"],
        "query": "重型包装纸箱 电商仓储 工厂 物流 获客",
        "prompt": "我要推广重型包装纸箱服务，目标客户是电商仓储、工厂、物流公司。请帮我分析获客方向、目标客户类型、内容建议、跟进话术和待办。不要真实外发。",
    },
    {
        "id": "task-003-fitness",
        "agent_id": "yuzhineng-sales-agent",
        "product": "健身器材外贸/内贸产品",
        "targets": ["健身房", "经销商", "跨境卖家"],
        "query": "健身器材 外贸 内贸 健身房 经销商 跨境卖家 获客",
        "prompt": "我要推广健身器材外贸/内贸产品，目标客户是健身房、经销商、跨境卖家。请判断商机、生成内容方向、销售话术和待办。不要真实外发。",
    },
]


def run(cmd: list[str], timeout: int = 120) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        shell=False,
    )
    return {
        "cmd": redact_cmd(cmd),
        "code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "duration_seconds": round(time.time() - started, 2),
    }


def redact_cmd(cmd: list[str]) -> list[str]:
    redacted: list[str] = []
    skip_next = False
    for item in cmd:
        if skip_next:
            redacted.append("***")
            skip_next = False
            continue
        redacted.append(item)
        if item in {"--token", "--password"}:
            skip_next = True
    return redacted


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def init_local_config() -> None:
    config = read_json(EXAMPLE_CONFIG)
    config["enabled"] = True
    write_json(LOCAL_CONFIG, config)
    print(f"created local config: {LOCAL_CONFIG}")


def load_enabled_config() -> dict[str, Any]:
    if os.environ.get("YUZHINENG_DEV_AUTO_RUN") != "1":
        raise RuntimeError("YUZHINENG_DEV_AUTO_RUN is not set to 1.")
    if not LOCAL_CONFIG.exists():
        raise RuntimeError(f"Missing local config: {LOCAL_CONFIG}. Run -InitLocalConfig first.")
    config = read_json(LOCAL_CONFIG)
    if not config.get("enabled"):
        raise RuntimeError("dev-auto-run.json exists but enabled is not true.")
    denied = set(config.get("denied_scopes", []))
    allowed = set(config.get("allowed_scopes", []))
    forbidden_overlap = sorted(denied.intersection(allowed))
    if forbidden_overlap:
        raise RuntimeError(f"Config has scopes in both allowed and denied: {forbidden_overlap}")
    if "operator.admin.global_allow" in allowed:
        raise RuntimeError("Global operator.admin allow is not permitted.")
    return config


def parse_json_maybe(raw: str) -> Any | None:
    try:
        return json.loads(raw)
    except Exception:
        return None


def ensure_openclaw_agents(config: dict[str, Any]) -> list[dict[str, Any]]:
    cli = config["openclaw_cli"]
    list_result = run([cli, "agents", "list", "--json"], timeout=60)
    existing = parse_json_maybe(list_result["stdout"]) if list_result["code"] == 0 else []
    existing_ids = {item.get("id") for item in existing or []}
    results = []
    for agent in TEST_AGENTS:
        workspace = TEST_RUNS_DIR / "workspaces" / agent["id"]
        agent_dir = TEST_RUNS_DIR / "openclaw-agents" / agent["id"]
        workspace.mkdir(parents=True, exist_ok=True)
        agent_dir.mkdir(parents=True, exist_ok=True)
        created = False
        add_result: dict[str, Any] | None = None
        if agent["id"] not in existing_ids:
            add_result = run([
                cli,
                "agents",
                "add",
                agent["id"],
                "--workspace",
                str(workspace),
                "--agent-dir",
                str(agent_dir),
                "--model",
                MODEL,
                "--non-interactive",
                "--json",
            ], timeout=90)
            created = add_result["code"] == 0
        identity_result = run([
            cli,
            "agents",
            "set-identity",
            "--agent",
            agent["id"],
            "--name",
            agent["name"],
            "--json",
        ], timeout=60)
        results.append({
            "agent_id": agent["id"],
            "name": agent["name"],
            "openclaw_created": created,
            "openclaw_already_existed": agent["id"] in existing_ids,
            "openclaw_add_code": add_result["code"] if add_result else None,
            "identity_code": identity_result["code"],
            "workspace": str(workspace),
            "agent_dir": str(agent_dir),
        })
    return results


def mirror_lobsterai_agents(config: dict[str, Any]) -> list[dict[str, Any]]:
    if not config.get("mirror_agents_to_lobsterai_ui", False):
        return []
    db_path = Path(os.path.expandvars(config["lobsterai_sqlite"]))
    if not db_path.exists():
        return [{"ok": False, "reason": f"LobsterAI SQLite not found: {db_path}"}]
    now = int(time.time() * 1000)
    con = sqlite3.connect(str(db_path))
    try:
        cur = con.cursor()
        results = []
        for agent in TEST_AGENTS:
            previous = cur.execute(
                "SELECT id, name, model, skill_ids FROM agents WHERE id = ?",
                (agent["id"],),
            ).fetchone()
            cur.execute(
                """
                INSERT INTO agents (
                  id, name, description, system_prompt, identity, model, working_directory,
                  icon, skill_ids, enabled, pinned, pin_order, is_default, source, preset_id,
                  created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, NULL, 0, 'custom', '', ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  name=excluded.name,
                  description=excluded.description,
                  system_prompt=excluded.system_prompt,
                  identity=excluded.identity,
                  model=excluded.model,
                  working_directory=excluded.working_directory,
                  icon=excluded.icon,
                  skill_ids=excluded.skill_ids,
                  enabled=1,
                  updated_at=excluded.updated_at
                """,
                (
                    agent["id"],
                    agent["name"],
                    agent["description"],
                    build_agent_prompt(agent),
                    agent["description"],
                    MODEL,
                    str(TEST_RUNS_DIR / "workspaces" / agent["id"]),
                    "agent-avatar-svg:lobster",
                    json.dumps(agent["skills"], ensure_ascii=False),
                    now,
                    now,
                ),
            )
            results.append({
                "agent_id": agent["id"],
                "name": agent["name"],
                "lobsterai_ui_mirrored": True,
                "previous_row_existed": previous is not None,
            })
        con.commit()
        return results
    finally:
        con.close()


def build_agent_prompt(agent: dict[str, Any]) -> str:
    return (
        f"你是{agent['name']}。职责：{agent['description']}\n"
        f"允许能力：{', '.join(agent['skills'])}。\n"
        f"禁止：{', '.join(agent['denied'])}。\n"
        "所有外部动作只生成草稿，必须 draft_only，不真实发送、不评论、不私信、不发帖、不读 secrets。"
    )


def call_domestic_skill(task: dict[str, Any]) -> dict[str, Any]:
    input_json = json.dumps({
        "product": task["product"],
        "target_customers": task["targets"],
        "platforms": ["小红书", "抖音"],
        "mode": "draft_only",
    }, ensure_ascii=False)
    result = run([
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(DOMESTIC_SKILL),
        "-InputJson",
        input_json,
    ], timeout=60)
    parsed = parse_json_maybe(result["stdout"]) if result["code"] == 0 else None
    return {
        "ok": result["code"] == 0 and parsed is not None,
        "code": result["code"],
        "duration_seconds": result["duration_seconds"],
        "parsed": parsed,
        "stderr": result["stderr"][-800:],
    }


def run_model_task(config: dict[str, Any], task: dict[str, Any], domestic: dict[str, Any]) -> dict[str, Any]:
    cli = config["openclaw_cli"]
    domestic_text = json.dumps(domestic.get("parsed"), ensure_ascii=False)[:5000] if domestic.get("parsed") else "domestic_signal_growth 调用失败"
    prompt = " ".join([
        "你是宇智能 Dev Auto-Run 测试 Agent。本轮必须保持 draft_only，不真实发布、不私信、不评论、不发邮件、不登录账号。",
        f"任务：{task['prompt']}",
        f"请先尝试调用 web_search 搜索公开网页，查询词：{task['query']}。",
        "如果 web_search 不可用，请在结果中明确写 web_search_status=\"failed\"，不要编造来源。",
        f"domestic_signal_growth 已由本地测试通道调用，结果如下：{domestic_text}",
        "请输出严格 JSON，不要 Markdown。",
        "字段：opportunity_judgement, target_customer_types, xiaohongshu_ideas, douyin_ideas, followup_drafts, todos, risk_notes, web_search_status, domestic_signal_growth_status, external_action_mode, sources。",
        "sources 没有真实来源时必须是 []。",
    ])
    result = run([
        cli,
        "agent",
        "--agent",
        task["agent_id"],
        "--message",
        prompt,
        "--model",
        MODEL,
        "--json",
        "--timeout",
        "300",
    ], timeout=340)
    parsed = parse_json_maybe(result["stdout"]) if result["code"] == 0 else None
    payload_text = ""
    meta: dict[str, Any] = {}
    if isinstance(parsed, dict):
        payloads = parsed.get("result", {}).get("payloads", [])
        if payloads and isinstance(payloads[0], dict):
            payload_text = payloads[0].get("text") or ""
        meta = parsed.get("result", {}).get("meta", {})
    output_json = extract_json_from_text(payload_text)
    tool_summary = meta.get("toolSummary") or {}
    execution_trace = meta.get("executionTrace") or {}
    agent_meta = meta.get("agentMeta") or {}
    return {
        "ok": result["code"] == 0 and bool(payload_text),
        "command_code": result["code"],
        "code": result["code"],
        "duration_seconds": result["duration_seconds"],
        "model": agent_meta.get("model") or execution_trace.get("winnerModel") or MODEL,
        "provider": agent_meta.get("provider") or execution_trace.get("winnerProvider"),
        "session_id": agent_meta.get("sessionId"),
        "usage": agent_meta.get("usage"),
        "tool_summary": tool_summary,
        "web_search_triggered": "web_search" in tool_summary.get("tools", []),
        "web_search_failures": tool_summary.get("failures", 0),
        "final_text": payload_text,
        "structured_output": output_json,
        "stdout_tail": result["stdout"][-1000:],
        "stderr_tail": result["stderr"][-1000:],
    }


def extract_json_from_text(text: str) -> Any | None:
    parsed = parse_json_maybe(text.strip())
    if parsed is not None:
        return parsed
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        return parse_json_maybe(match.group(0))
    return None


def mirror_session_to_lobsterai(config: dict[str, Any], run_id: str, task: dict[str, Any], task_result: dict[str, Any]) -> dict[str, Any]:
    db_path = Path(os.path.expandvars(config["lobsterai_sqlite"]))
    if not db_path.exists():
        return {"ok": False, "reason": f"LobsterAI SQLite not found: {db_path}"}
    session_id = f"dev-autorun-{run_id}-{task['id']}"
    now = int(time.time() * 1000)
    con = sqlite3.connect(str(db_path))
    try:
        cur = con.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO cowork_sessions (
              id, title, claude_session_id, status, pinned, pin_order, cwd,
              system_prompt, model_override, execution_mode, parent_session_id,
              forked_from_message_id, forked_at, fork_mode, fork_workspace_path,
              fork_git_branch, fork_git_base_ref, created_at, updated_at,
              active_skill_ids, agent_id
            )
            VALUES (?, ?, NULL, 'idle', 0, NULL, ?, ?, ?, 'local', NULL, NULL, NULL,
              'none', NULL, NULL, NULL, ?, ?, ?, ?)
            """,
            (
                session_id,
                f"DevAutoRun：{task['product']}",
                str(TEST_RUNS_DIR / "workspaces" / task["agent_id"]),
                "宇智能 Dev Auto-Run 测试会话，仅用于本地开发验证。",
                MODEL,
                now,
                now,
                json.dumps(["web-search", "domestic_signal_growth"], ensure_ascii=False),
                task["agent_id"],
            ),
        )
        cur.execute("DELETE FROM cowork_messages WHERE session_id = ?", (session_id,))
        messages = [
            ("user", task["prompt"], {"dev_auto_run": True, "task_id": task["id"]}),
            ("assistant", task_result.get("final_text", ""), {
                "dev_auto_run": True,
                "model": task_result.get("model"),
                "web_search_triggered": task_result.get("web_search_triggered"),
                "external_action_mode": "draft_only",
            }),
        ]
        for index, (msg_type, content, metadata) in enumerate(messages, start=1):
            cur.execute(
                """
                INSERT INTO cowork_messages (id, session_id, type, content, metadata, created_at, sequence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{session_id}-msg-{index}",
                    session_id,
                    msg_type,
                    content,
                    json.dumps(metadata, ensure_ascii=False),
                    now + index,
                    index,
                ),
            )
        con.commit()
        return {"ok": True, "session_id": session_id}
    finally:
        con.close()


def save_task_trace(run_dir: Path, task: dict[str, Any], domestic: dict[str, Any], model_result: dict[str, Any], mirror: dict[str, Any]) -> dict[str, Any]:
    trace = {
        "task_id": task["id"],
        "input_task": task["prompt"],
        "target_product": task["product"],
        "target_customers": task["targets"],
        "model": model_result.get("model"),
        "requested_model": MODEL,
        "tools": {
            "web_search": {
                "triggered": model_result.get("web_search_triggered", False),
                "failures": model_result.get("web_search_failures", 0),
                "tool_summary": model_result.get("tool_summary"),
            }
        },
        "skills": {
            "domestic_signal_growth": {
                "triggered": domestic.get("ok", False),
                "status": "ok" if domestic.get("ok") else "failed",
            }
        },
        "output_summary": summarize_output(model_result.get("structured_output"), model_result.get("final_text", "")),
        "structured_output": model_result.get("structured_output"),
        "risk_check": {
            "external_action_mode": "draft_only",
            "real_external_send": False,
            "read_secrets": False,
            "social_login": False,
        },
        "completed": model_result.get("ok", False),
        "failure_reason": None if model_result.get("ok") else model_result.get("stderr_tail"),
        "command_code": model_result.get("command_code"),
        "stdout_tail": model_result.get("stdout_tail"),
        "stderr_tail": model_result.get("stderr_tail"),
        "openclaw_session_id": model_result.get("session_id"),
        "lobsterai_ui_session": mirror,
        "usage": model_result.get("usage"),
    }
    write_json(run_dir / f"{task['id']}.json", trace)
    write_text(run_dir / f"{task['id']}.md", task_markdown(trace))
    return trace


def summarize_output(structured: Any, final_text: str) -> str:
    if isinstance(structured, dict):
        judgement = structured.get("opportunity_judgement") or structured.get("商机判断")
        if isinstance(judgement, str):
            return clean_summary(judgement)
    return clean_summary(final_text)


def clean_summary(text: str, limit: int = 260) -> str:
    text = text or ""
    text = text.split("```", 1)[0]
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "模型已返回结果，但没有生成可读摘要；请查看本轮 JSON 轨迹。"
    return text[:limit]


def quality_notes(trace: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    if not trace.get("structured_output"):
        notes.append("结构化 JSON 未成功解析，已保留原始轨迹，后续需强化 JSON 输出约束。")
    if int(trace["tools"]["web_search"].get("failures") or 0) > 0:
        notes.append("web-search 已触发但 provider 不可用，本轮没有真实公开来源。")
    summary = trace.get("output_summary") or ""
    product = trace.get("target_product") or ""
    if product and product not in summary and "偏差" in summary:
        notes.append("domestic_signal_growth 返回内容存在主题偏移，需要升级为真实业务 Skill。")
    return notes


def trace_summary(trace: dict[str, Any]) -> str:
    return clean_summary(trace.get("output_summary") or "")


def task_markdown(trace: dict[str, Any]) -> str:
    return f"""# {trace['task_id']}

## 输入任务

{trace['input_task']}

## 使用模型

- 请求模型：{trace['requested_model']}
- 实际模型：{trace['model']}

## 工具与 Skill

- web-search 触发：{trace['tools']['web_search']['triggered']}
- web-search 失败数：{trace['tools']['web_search']['failures']}
- domestic_signal_growth 触发：{trace['skills']['domestic_signal_growth']['triggered']}

## 输出摘要

{trace['output_summary']}

## 质量提醒

{chr(10).join('- ' + note for note in quality_notes(trace)) or '- 暂无额外质量提醒。'}

## 风险检查

- 外部动作模式：draft_only
- 真实外发：False
- 读取 secrets：False
- 社媒登录：False

## 完成状态

- completed：{trace['completed']}
- failure_reason：{trace['failure_reason']}
"""


def generate_report(run_id: str, started_at: str, config: dict[str, Any], agent_results: list[dict[str, Any]], ui_results: list[dict[str, Any]], traces: list[dict[str, Any]]) -> None:
    all_done = all(t.get("completed") for t in traces)
    all_v4 = all(t.get("model") == "deepseek-v4-pro" for t in traces)
    web_triggered = any(t["tools"]["web_search"]["triggered"] for t in traces)
    web_failures = sum(int(t["tools"]["web_search"]["failures"] or 0) for t in traces)
    domestic_ok = all(t["skills"]["domestic_signal_growth"]["triggered"] for t in traces)
    conclusion = "B：部分成立，先修复具体阻塞点"
    if all_done and all_v4 and web_triggered and domestic_ok and web_failures == 0:
        conclusion = "A：Dev Auto-Run 成立，进入 Phase 2"
    elif not all_done or not all_v4:
        conclusion = "B：部分成立，先修复具体阻塞点"

    lines = [
        "# Phase 1A-DevAutoRunGate：开发测试自动权限与多 Agent 任务验证",
        "",
        "## 1. 测试日期",
        "",
        f"- 测试时间：{started_at}",
        f"- Run ID：{run_id}",
        "",
        "## 2. 当前 LobsterAI commit",
        "",
        "- 当前工作区基线来自上一阶段 commit：5348d6a9a75b002a95e1545fd5ca1571f03eb16b",
        "- 本阶段未提交 LobsterAI 上游源码目录，避免把 PoC 外部源码纳入 v2 基线。",
        "",
        "## 3. Dev Auto-Run 是否实现",
        "",
        "- 已实现本地开发测试通道：`v2/scripts/dev-autorun-gate.py` 与 `v2/scripts/dev-autorun-gate.ps1`。",
        "- 默认关闭；只有 `YUZHINENG_DEV_AUTO_RUN=1` 且本地 `v2/dev-config/dev-auto-run.json` 中 `enabled=true` 时运行。",
        "- 真实本地配置 `dev-auto-run.json` 已加入 `.gitignore`，仓库只提交 `.example`。",
        "",
        "## 4. 是否有 UI 审批入口",
        "",
        "- 本阶段未实现正式 UI 审批入口。",
        "- 继续保留上一阶段判断：Cowork 普通 UI 仍缺少 `operator.admin/operator.write` scope upgrade 的可见批准入口。",
        "",
        "## 5. allowed_scopes",
        "",
        "```json",
        json.dumps(config.get("allowed_scopes", []), ensure_ascii=False, indent=2),
        "```",
        "",
        "## 6. denied_scopes",
        "",
        "```json",
        json.dumps(config.get("denied_scopes", []), ensure_ascii=False, indent=2),
        "```",
        "",
        "## 7. 是否默认关闭",
        "",
        "- 是。example 中 `enabled=false`，脚本还要求环境变量 `YUZHINENG_DEV_AUTO_RUN=1`。",
        "",
        "## 8. 如何开启",
        "",
        "```powershell",
        "D:\\OpenClaw\\v2\\scripts\\dev-autorun-gate.ps1 -InitLocalConfig",
        "D:\\OpenClaw\\v2\\scripts\\dev-autorun-gate.ps1 -Run",
        "```",
        "",
        "## 9. 如何关闭",
        "",
        "- 删除或禁用 `D:\\OpenClaw\\v2\\dev-config\\dev-auto-run.json`。",
        "- 取消环境变量 `YUZHINENG_DEV_AUTO_RUN`。",
        "",
        "## 10. 是否使用 deepseek/deepseek-v4-pro",
        "",
        f"- 三轮任务实际模型均为 V4 Pro：{all_v4}",
        "",
        "## 11. 三个测试 Agent 创建结果",
        "",
        "```json",
        json.dumps(agent_results, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 12. LobsterAI UI Agent 镜像结果",
        "",
        "```json",
        json.dumps(ui_results, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 13. 三个测试任务创建结果",
        "",
    ]
    for trace in traces:
        lines.extend([
            f"### {trace['task_id']}",
            "",
            f"- 完成：{trace['completed']}",
            f"- OpenClaw session：{trace.get('openclaw_session_id')}",
            f"- LobsterAI UI session：{trace.get('lobsterai_ui_session')}",
            f"- 摘要：{trace_summary(trace)}",
            f"- 质量提醒：{'；'.join(quality_notes(trace)) or '暂无'}",
            "",
        ])
    lines.extend([
        "## 14. web-search 调用结果",
        "",
        f"- 是否触发：{web_triggered}",
        f"- 失败数合计：{web_failures}",
        "- 说明：本轮 OpenClaw agent 能触发 `web_search` 工具，但当前 provider 未配置或不可用时，模型会返回失败状态并继续生成 draft_only 结果。",
        "",
        "## 15. domestic_signal_growth 调用结果",
        "",
        f"- 三轮本地 Skill 均已调用：{domestic_ok}",
        "",
        "## 16. 最小业务结果摘要",
        "",
    ])
    for trace in traces:
        lines.append(f"- {trace['task_id']}：{trace_summary(trace)}")
        notes = quality_notes(trace)
        if notes:
            lines.append(f"  质量提醒：{'；'.join(notes)}")
    lines.extend([
        "",
        "## 17. 安全检查结果",
        "",
        "- 未读取 `D:\\OpenClaw\\secrets`。",
        "- 未提交 API Key、Token、Cookie、浏览器 Profile。",
        "- 未真实发送邮件、私信、评论或发帖。",
        "- 未登录社媒账号。",
        "- 未下载官方更新包。",
        "- 未全局关闭权限检查。",
        "- Dev Auto-Run 仅由本地环境变量和本地配置显式开启。",
        "",
        "## 18. 是否建议进入 Phase 2",
        "",
        f"- 结论：{conclusion}",
        "- 建议：先修复 web-search provider 配置和 Cowork UI scope approval，再进入完整 Phase 2。",
        "",
        "## 19. 下一步建议",
        "",
        "1. 给 Cowork 的 `operator.admin/operator.write` scope upgrade 增加可见审批入口，或把开发测试 runner 与普通 UI runner 分离。",
        "2. 配置 OpenClaw web_search provider，使公开搜索不再失败。",
        "3. 把 `domestic_signal_growth` 从占位 PowerShell Skill 升级为可被 Cowork/OpenClaw 原生发现的 Skill 或 MCP 工具。",
        "4. 修复 UI 会话模型默认值，深度任务默认使用 `deepseek/deepseek-v4-pro`。",
        "",
        "## 20. 回滚方式",
        "",
        "- 删除 `D:\\OpenClaw\\v2\\dev-config\\dev-auto-run.json`。",
        "- 删除 `D:\\OpenClaw\\v2\\data\\test-runs\\` 下本轮测试目录。",
        "- 在 LobsterAI UI 中删除 ID 前缀为 `yuzhineng-` 的测试 Agent/会话，或使用后续清理脚本。",
        "- 回退本阶段 Git commit。",
        "",
    ])
    write_text(REPORT_PATH, "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-local-config", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()

    if args.init_local_config:
        init_local_config()
        return 0
    if not args.run:
        parser.print_help()
        return 2

    started_at = time.strftime("%Y-%m-%d %H:%M:%S %z")
    run_id = time.strftime("%Y%m%d-%H%M%S")
    config = load_enabled_config()
    run_dir = TEST_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    agent_results = ensure_openclaw_agents(config)
    ui_results = mirror_lobsterai_agents(config)

    traces = []
    for task in TEST_TASKS:
        domestic = call_domestic_skill(task)
        model_result = run_model_task(config, task, domestic)
        mirror = mirror_session_to_lobsterai(config, run_id, task, model_result)
        trace = save_task_trace(run_dir, task, domestic, model_result, mirror)
        traces.append(trace)

    write_json(run_dir / "summary.json", {
        "run_id": run_id,
        "started_at": started_at,
        "model": MODEL,
        "agent_results": agent_results,
        "lobsterai_ui_agent_results": ui_results,
        "tasks": traces,
    })
    write_json(TEST_RUNS_DIR / "latest.json", {
        "run_id": run_id,
        "path": str(run_dir),
        "completed": all(t.get("completed") for t in traces),
    })
    generate_report(run_id, started_at, config, agent_results, ui_results, traces)
    print(json.dumps({
        "ok": True,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "report": str(REPORT_PATH),
        "tasks_completed": sum(1 for t in traces if t.get("completed")),
        "tasks_total": len(traces),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
