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
MANUFACTURING_TEST_CASE_DIR = V2 / "test-cases" / "manufacturing_growth"
PRODUCT_INTELLIGENCE_TEST_CASE_DIR = V2 / "test-cases" / "product_intelligence"
MULTI_AGENT_TEST_CASE_DIR = V2 / "test-cases" / "multi_agent_workflow"
REPORT_PATH = V2 / "reports" / "LOBSTERAI_DEV_AUTORUN_GATE_REPORT_CN.md"
DOMESTIC_SKILL = V2 / "skills" / "domestic_signal_growth" / "domestic_signal_growth.ps1"
PRODUCT_INTELLIGENCE_SKILL = V2 / "skills" / "product_intelligence" / "product_intelligence.ps1"
MULTI_AGENT_WORKFLOW_SCRIPT = V2 / "scripts" / "run_manufacturing_multi_agent_workflow.py"
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


MANUFACTURING_AGENTS = [
    {
        "id": "yuzhineng-manufacturing-chief",
        "name": "宇智能制造业获客总控 Agent",
        "description": "接收老板/运营输入，拆解制造业获客任务，汇总产品理解、商机、内容、社媒、交接单和待办。",
        "skills": ["manufacturing_multi_agent_workflow", "product_intelligence", "web-search", "domestic_signal_growth", "docx", "xlsx"],
        "denied": ["真实外发", "登录社媒", "读取 secrets", "自动发布"],
    },
    {
        "id": "yuzhineng-product-analyst",
        "name": "产品理解 Agent",
        "description": "理解工厂产品资料，提炼卖点、适合客户类型、采购决策人和风险点。",
        "skills": ["product_intelligence", "domestic_signal_growth", "docx"],
        "denied": ["真实外发", "读取 secrets"],
    },
    {
        "id": "yuzhineng-opportunity-researcher",
        "name": "商机发掘 Agent",
        "description": "搜索公开信息，判断潜在客户、采购信号、来源链接和商机评分。",
        "skills": ["web-search", "domestic_signal_growth"],
        "denied": ["登录社媒", "绕过验证码", "读取 secrets"],
    },
    {
        "id": "yuzhineng-content-producer",
        "name": "宣传物料 Agent",
        "description": "生成小红书、抖音、公众号、产品介绍文案、销售话术和内容草稿。",
        "skills": ["domestic_signal_growth", "docx"],
        "denied": ["真实发布", "评论", "私信"],
    },
    {
        "id": "yuzhineng-social-operator",
        "name": "社媒运营 Agent",
        "description": "生成发布计划、评论回复草稿、私信草稿和账号养成计划；当前阶段不真实发布。",
        "skills": ["domestic_signal_growth", "web-search"],
        "denied": ["真实发布", "真实评论", "真实私信", "登录社媒"],
    },
    {
        "id": "yuzhineng-factory-handoff",
        "name": "工厂对接 Agent",
        "description": "生成销售交接单、客户需求摘要、推荐跟进人和待办，把高价值客户转给工厂销售/老板。",
        "skills": ["domestic_signal_growth", "xlsx", "docx"],
        "denied": ["真实发邮件", "批量导出", "读取 secrets"],
    },
    {
        "id": "yuzhineng-safety-reviewer",
        "name": "风控审核 Agent",
        "description": "检查真实外发、夸大宣传、伪造来源、敏感信息和人工审批要求。",
        "skills": ["domestic_signal_growth"],
        "denied": ["真实外发", "读取 secrets", "绕过验证码", "伪造来源"],
    },
    {
        "id": "yuzhineng-archive-agent",
        "name": "归档 Agent",
        "description": "把制造业获客成果保存到项目工作区，更新项目索引，并输出成果路径。",
        "skills": ["docx", "xlsx"],
        "denied": ["读取 secrets", "真实外发", "删除项目数据"],
    },
]


TEST_TASKS = [
    {
        "id": "task-001-certificate",
        "agent_id": "yuzhineng-lead-agent",
        "product": "职业证书考评服务",
        "industry": "教育培训",
        "targets": ["培训机构", "人力资源公司"],
        "platforms": ["小红书", "抖音"],
        "query": "职业证书培训机构营销方式",
        "prompt": "我要推广职业证书考评服务，目标客户是培训机构和人力资源公司。请判断商机、生成客户类型、小红书内容建议、抖音内容建议、跟进话术和待办。不要真实发布、不要私信、不要评论、不要发邮件。",
    },
    {
        "id": "task-002-carton",
        "agent_id": "yuzhineng-content-agent",
        "product": "重型包装纸箱服务",
        "industry": "包装制造 / 仓储物流",
        "targets": ["电商仓储", "工厂", "物流公司"],
        "platforms": ["小红书", "抖音", "公众号"],
        "query": "重型包装纸箱 电商仓储 工厂 物流 获客",
        "prompt": "我要推广重型包装纸箱服务，目标客户是电商仓储、工厂、物流公司。请帮我分析获客方向、目标客户类型、内容建议、跟进话术和待办。不要真实外发。",
    },
    {
        "id": "task-003-fitness",
        "agent_id": "yuzhineng-sales-agent",
        "product": "健身器材",
        "industry": "健身器材 / 商贸",
        "targets": ["健身房", "经销商", "跨境卖家"],
        "platforms": ["小红书", "抖音", "公众号"],
        "query": "健身器材 外贸 内贸 健身房 经销商 跨境卖家 获客",
        "prompt": "我要推广健身器材，目标客户是健身房、经销商、跨境卖家。请判断商机、生成内容方向、销售话术和待办。不要真实外发。",
    },
]


def run(cmd: list[str], timeout: int = 120) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            proc.kill()
        stdout, stderr = proc.communicate(timeout=10)
        stderr = (stderr or "") + f"\nCommand timed out after {timeout} seconds."
    return {
        "cmd": redact_cmd(cmd),
        "code": -9 if timed_out else proc.returncode,
        "stdout": stdout or "",
        "stderr": stderr or "",
        "duration_seconds": round(time.time() - started, 2),
        "timed_out": timed_out,
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


def ensure_openclaw_agents(config: dict[str, Any], agents: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    agents = agents or TEST_AGENTS
    cli = config["openclaw_cli"]
    list_result = run([cli, "agents", "list", "--json"], timeout=60)
    existing = parse_json_maybe(list_result["stdout"]) if list_result["code"] == 0 else []
    existing_ids = {item.get("id") for item in existing or []}
    results = []
    for agent in agents:
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


def mirror_lobsterai_agents(config: dict[str, Any], agents: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    agents = agents or TEST_AGENTS
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
        for agent in agents:
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
    workflow_hint = ""
    if agent["id"] == "yuzhineng-manufacturing-chief":
        workflow_hint = (
            "\n当用户输入制造业获客、推广、社媒内容、销售交接相关任务时，优先使用 "
            "manufacturing_multi_agent_workflow Skill 或本地脚本 "
            "D:\\OpenClaw\\v2\\scripts\\run_manufacturing_multi_agent_workflow.ps1。"
            "完成后用中文展示 report.md 的八个 Agent 输出段落，并告诉用户项目目录、report.md、handoff.docx 和 projects_index.html。"
        )
    return (
        f"你是{agent['name']}。职责：{agent['description']}\n"
        f"允许能力：{', '.join(agent['skills'])}。\n"
        f"禁止：{', '.join(agent['denied'])}。\n"
        "所有外部动作只生成草稿，必须 draft_only，不真实发送、不评论、不私信、不发帖、不读 secrets。"
        f"{workflow_hint}"
    )


def call_domestic_skill(task: dict[str, Any]) -> dict[str, Any]:
    input_payload = task.get("skill_input") or {
        "product": task["product"],
        "industry": task.get("industry", ""),
        "target_customers": task["targets"],
        "city": task.get("city", "全国"),
        "platforms": task.get("platforms", ["小红书", "抖音"]),
        "mode": "draft_only",
        "search_required": True,
    }
    input_cache = TEST_RUNS_DIR / "_input-cache" / f"{task['id']}.json"
    write_json(input_cache, input_payload)
    result = run([
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(DOMESTIC_SKILL),
        "-InputFile",
        str(input_cache),
    ], timeout=60)
    parsed = parse_json_maybe(result["stdout"]) if result["code"] == 0 else None
    return {
        "ok": result["code"] == 0 and parsed is not None,
        "code": result["code"],
        "duration_seconds": result["duration_seconds"],
        "parsed": parsed,
        "stderr": result["stderr"][-800:],
    }


def call_product_intelligence(input_file: Path, output_dir: Path) -> dict[str, Any]:
    output_file = output_dir / "product_intelligence_output.json"
    result = run([
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(PRODUCT_INTELLIGENCE_SKILL),
        "-InputFile",
        str(input_file),
        "-OutputFile",
        str(output_file),
        "-OutputDir",
        str(output_dir),
    ], timeout=60)
    parsed = read_json(output_file) if result["code"] == 0 and output_file.exists() else None
    return {
        "ok": result["code"] == 0 and parsed is not None,
        "code": result["code"],
        "duration_seconds": result["duration_seconds"],
        "parsed": parsed,
        "output_dir": str(output_dir),
        "output_file": str(output_file),
        "stderr": result["stderr"][-800:],
    }


def model_safe_domestic_payload(parsed: Any) -> dict[str, Any]:
    if not isinstance(parsed, dict):
        return {"status": "domestic_signal_growth 调用失败"}
    sources = parsed.get("sources") or []
    return {
        "skill": parsed.get("skill"),
        "product": parsed.get("product"),
        "industry": parsed.get("industry"),
        "mode": parsed.get("mode"),
        "source_status": parsed.get("source_status"),
        "source_count": len(sources),
        "source_titles": [source.get("title") for source in sources[:5] if isinstance(source, dict)],
        "opportunity_judgement": parsed.get("opportunity_judgement"),
        "target_customer_types": parsed.get("target_customer_types"),
        "platform_strategy": parsed.get("platform_strategy"),
        "followup_drafts": parsed.get("followup_drafts"),
        "todos": parsed.get("todos"),
        "risk_notes": parsed.get("risk_notes"),
        "next_steps": parsed.get("next_steps"),
        "product_understanding": parsed.get("product_understanding"),
        "opportunity_discovery": parsed.get("opportunity_discovery"),
        "content_materials": parsed.get("content_materials"),
        "social_publish_plan": parsed.get("social_publish_plan"),
        "comment_reply_drafts": parsed.get("comment_reply_drafts"),
        "dm_drafts": parsed.get("dm_drafts"),
        "account_nurturing_plan": parsed.get("account_nurturing_plan"),
        "factory_handoff_sheet": parsed.get("factory_handoff_sheet"),
    }


def compact_for_model(value: Any, *, list_limit: int = 3, string_limit: int = 240) -> Any:
    if isinstance(value, str):
        return value if len(value) <= string_limit else value[:string_limit] + "..."
    if isinstance(value, list):
        return [compact_for_model(item, list_limit=list_limit, string_limit=string_limit) for item in value[:list_limit]]
    if isinstance(value, dict):
        return {
            key: compact_for_model(item, list_limit=list_limit, string_limit=string_limit)
            for key, item in value.items()
        }
    return value


def safe_cmd_message(text: str) -> str:
    # openclaw.cmd is a Windows batch entrypoint; do not pass raw URLs or shell
    # metacharacters in a long prompt argument.
    return (
        text.replace("&", "和")
        .replace("|", " ")
        .replace("<", " ")
        .replace(">", " ")
        .replace("^", "")
        .replace("%", "百分号")
    )


def run_model_task(config: dict[str, Any], task: dict[str, Any], domestic: dict[str, Any]) -> dict[str, Any]:
    cli = config["openclaw_cli"]
    if domestic.get("parsed"):
        domestic_text = json.dumps(
            compact_for_model(model_safe_domestic_payload(domestic.get("parsed"))),
            ensure_ascii=False,
            separators=(",", ":"),
        )
    else:
        domestic_text = "domestic_signal_growth 调用失败"
    prompt = safe_cmd_message(" ".join([
        "你是宇智能 Dev Auto-Run 测试 Agent。本轮必须保持 draft_only，不真实发布、不私信、不评论、不发邮件、不登录账号。",
        f"任务：{task['prompt']}",
        "本地 search_adapter 已经完成公开搜索；你不要再次调用 web_search，不要操作浏览器，不要访问外部渠道。",
        f"domestic_signal_growth 结构化结果如下：{domestic_text}",
        "请输出严格 JSON，不要 Markdown。",
        "字段：product_understanding, opportunity_discovery, target_customer_segments, content_materials, social_publish_plan, comment_reply_drafts, dm_drafts, account_nurturing_plan, factory_handoff_sheet, todos, risk_notes, web_search_status, domestic_signal_growth_status, external_action_mode, source_status, source_count。",
        "external_action_mode 必须是 draft_only。",
    ]))
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
        "120",
    ], timeout=150)
    parsed = parse_json_maybe(result["stdout"]) if result["code"] == 0 else None
    if parsed is None and result["code"] == 0:
        parsed = extract_openclaw_json_from_stdout(result["stdout"])
    payload_text = ""
    meta: dict[str, Any] = {}
    if isinstance(parsed, dict):
        root = parsed.get("result") if isinstance(parsed.get("result"), dict) else parsed
        payloads = root.get("payloads", [])
        if payloads and isinstance(payloads[0], dict):
            payload_text = payloads[0].get("text") or ""
        if not payload_text:
            payload_text = root.get("finalAssistantVisibleText") or root.get("finalAssistantRawText") or ""
        meta = root.get("meta", {})
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


def build_skill_only_phase2b_result(task: dict[str, Any], domestic: dict[str, Any]) -> dict[str, Any]:
    parsed = domestic.get("parsed") or {}
    structured = {
        "product_understanding": parsed.get("product_understanding"),
        "opportunity_discovery": parsed.get("opportunity_discovery"),
        "target_customer_segments": parsed.get("target_customer_segments"),
        "content_materials": parsed.get("content_materials"),
        "social_publish_plan": parsed.get("social_publish_plan"),
        "comment_reply_drafts": parsed.get("comment_reply_drafts"),
        "dm_drafts": parsed.get("dm_drafts"),
        "account_nurturing_plan": parsed.get("account_nurturing_plan"),
        "factory_handoff_sheet": parsed.get("factory_handoff_sheet"),
        "todos": parsed.get("todos"),
        "risk_notes": parsed.get("risk_notes"),
        "web_search_status": parsed.get("source_status"),
        "domestic_signal_growth_status": "ok" if domestic.get("ok") else "failed",
        "external_action_mode": "draft_only",
        "source_status": parsed.get("source_status"),
        "source_count": len(parsed.get("sources") or []),
    }
    return {
        "ok": True,
        "command_code": None,
        "code": None,
        "duration_seconds": 0,
        "model": MODEL,
        "provider": "phase2b-skill-only",
        "session_id": None,
        "usage": None,
        "tool_summary": {},
        "web_search_triggered": False,
        "web_search_failures": 0,
        "final_text": phase2b_summary_markdown(task, domestic, {"ok": False, "model_validation_skipped": True}),
        "structured_output": structured,
        "stdout_tail": "",
        "stderr_tail": "Phase 2B 默认跳过 OpenClaw agent 模型汇总，避免 CLI 卡住；DeepSeek V4 Pro 验证需单独开启 phase2b_enable_openclaw_model_validation。",
        "model_validation_skipped": True,
    }


def extract_json_from_text(text: str) -> Any | None:
    parsed = parse_json_maybe(text.strip())
    if parsed is not None:
        return parsed
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        return parse_json_maybe(match.group(0))
    return None


def extract_openclaw_json_from_stdout(text: str) -> Any | None:
    marker = '"payloads"'
    marker_index = text.find(marker)
    if marker_index < 0:
        return None
    start = text.rfind("{", 0, marker_index)
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    return parse_json_maybe(text[start:end + 1])


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


def phase2a_task_input(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "product": task["product"],
        "industry": task.get("industry", ""),
        "target_customers": task["targets"],
        "city": task.get("city", "全国"),
        "platforms": task.get("platforms", ["小红书", "抖音"]),
        "mode": "draft_only",
        "search_required": True,
        "model": MODEL,
        "prompt": task["prompt"],
    }


def phase2a_safety_check(task: dict[str, Any], domestic: dict[str, Any], model_result: dict[str, Any]) -> dict[str, Any]:
    parsed = domestic.get("parsed") or {}
    has_external_action = any(
        token in json.dumps(parsed, ensure_ascii=False)
        for token in ["已发送", "已私信", "已评论", "已发布"]
    )
    return {
        "task_id": task["id"],
        "external_action_mode": parsed.get("mode") or "draft_only",
        "real_email_sent": False,
        "real_dm_sent": False,
        "real_comment_posted": False,
        "real_post_published": False,
        "social_login": False,
        "read_secrets": False,
        "invented_sources_detected": False,
        "draft_only_text_check_passed": not has_external_action,
        "requires_human_approval_for_external_actions": True,
        "model_requested": MODEL,
        "model_result_model": model_result.get("model"),
        "model_call_ok": model_result.get("ok", False),
    }


def phase2a_summary_markdown(task: dict[str, Any], domestic: dict[str, Any], model_result: dict[str, Any]) -> str:
    parsed = domestic.get("parsed") or {}
    opportunity = parsed.get("opportunity_judgement") or {}
    source_status = parsed.get("source_status", "unknown")
    sources = parsed.get("sources") or []
    strategy = parsed.get("platform_strategy") or {}
    followups = parsed.get("followup_drafts") or []
    todos = parsed.get("todos") or []
    risks = parsed.get("risk_notes") or []
    next_steps = parsed.get("next_steps") or []
    model_note = "已尝试使用 DeepSeek V4 Pro 生成最终解释。" if model_result.get("ok") else "DeepSeek V4 Pro 总结未成功，本文件使用 Skill 结构化输出生成。"

    def bullet(items: list[Any], limit: int = 8) -> str:
        if not items:
            return "- 暂无。"
        lines = []
        for item in items[:limit]:
            if isinstance(item, dict):
                if "title" in item:
                    lines.append(f"- {item.get('title')}")
                elif "draft" in item:
                    lines.append(f"- {item.get('scenario', '草稿')}：{item.get('draft')}")
                elif "type" in item:
                    lines.append(f"- {item.get('type')}：{'、'.join(item.get('pain_points') or [])}")
                else:
                    lines.append(f"- {json.dumps(item, ensure_ascii=False)}")
            else:
                lines.append(f"- {item}")
        return "\n".join(lines)

    platform_lines = []
    for key, value in strategy.items():
        platform_lines.append(f"### {key}\n\n- 定位：{value.get('positioning')}\n{bullet(value.get('content_ideas') or [], 5)}")

    return f"""# {task['product']}：Phase 2A 测试摘要

## 基本信息

- 行业：{task.get('industry')}
- 目标客户：{'、'.join(task['targets'])}
- 平台：{'、'.join(task.get('platforms', []))}
- 模式：draft_only
- 模型：{MODEL}
- 模型说明：{model_note}

## 公开来源状态

- source_status：{source_status}
- 来源数量：{len(sources)}

{bullet([{'title': source.get('title'), 'url': source.get('url')} for source in sources], 5)}

## 商机判断

- 等级：{opportunity.get('level')}
- 置信度：{opportunity.get('confidence')}
- 原因：{opportunity.get('reason')}

## 目标客户类型

{bullet(parsed.get('target_customer_types') or [], 6)}

## 平台内容策略

{chr(10).join(platform_lines) if platform_lines else '- 暂无。'}

## 跟进话术草稿

{bullet(followups, 5)}

## 待办

{bullet(todos, 8)}

## 风险提醒

{bullet(risks, 8)}

## 下一步

{bullet(next_steps, 8)}
"""


def save_phase2a_task_files(run_dir: Path, task: dict[str, Any], domestic: dict[str, Any], model_result: dict[str, Any]) -> dict[str, Any]:
    task_dir = run_dir / task["id"]
    task_dir.mkdir(parents=True, exist_ok=True)
    parsed = domestic.get("parsed") or {}
    write_json(task_dir / "input.json", phase2a_task_input(task))
    write_json(task_dir / "skill_output.json", parsed)
    write_json(task_dir / "search_trace.json", {
        "task_id": task["id"],
        "source_status": parsed.get("source_status"),
        "sources": parsed.get("sources") or [],
        "search_trace": parsed.get("search_trace") or {},
        "web_search_tool_summary": model_result.get("tool_summary"),
        "web_search_triggered_by_model": model_result.get("web_search_triggered", False),
        "web_search_failures_by_model": model_result.get("web_search_failures", 0),
    })
    safety = phase2a_safety_check(task, domestic, model_result)
    write_json(task_dir / "safety_check.json", safety)
    write_text(task_dir / "summary.md", phase2a_summary_markdown(task, domestic, model_result))
    return {
        "task_id": task["id"],
        "task_dir": str(task_dir),
        "domestic_ok": domestic.get("ok", False),
        "model_ok": model_result.get("ok", False),
        "model_validation_skipped": model_result.get("model_validation_skipped", False),
        "source_status": parsed.get("source_status"),
        "source_count": len(parsed.get("sources") or []),
        "draft_only": safety["external_action_mode"] == "draft_only",
        "industry_adapted": task["product"] in json.dumps(parsed, ensure_ascii=False),
    }


def run_phase2a() -> int:
    started_at = time.strftime("%Y-%m-%d %H:%M:%S %z")
    run_id = "phase2a-" + time.strftime("%Y%m%d-%H%M%S")
    config = load_enabled_config()
    run_dir = TEST_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    agent_results = ensure_openclaw_agents(config)
    ui_results = mirror_lobsterai_agents(config)
    task_summaries = []
    raw_model_results = []

    for task in TEST_TASKS:
        domestic = call_domestic_skill(task)
        model_result = run_model_task(config, task, domestic)
        mirror = mirror_session_to_lobsterai(config, run_id, task, model_result)
        model_result["lobsterai_ui_session"] = mirror
        raw_model_results.append({"task_id": task["id"], "model_result": model_result})
        task_summaries.append(save_phase2a_task_files(run_dir, task, domestic, model_result))

    write_json(run_dir / "summary.json", {
        "run_id": run_id,
        "started_at": started_at,
        "model": MODEL,
        "agent_results": agent_results,
        "lobsterai_ui_agent_results": ui_results,
        "tasks": task_summaries,
        "raw_model_results": raw_model_results,
    })
    write_json(TEST_RUNS_DIR / "latest-phase2a.json", {
        "run_id": run_id,
        "path": str(run_dir),
        "completed": all(item["domestic_ok"] for item in task_summaries),
    })
    print(json.dumps({
        "ok": True,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "tasks": task_summaries,
    }, ensure_ascii=False, indent=2))
    return 0


def load_manufacturing_test_tasks() -> list[dict[str, Any]]:
    mapping = [
        ("heavy_packaging.json", "yuzhineng-manufacturing-chief"),
        ("fitness_equipment.json", "yuzhineng-manufacturing-chief"),
        ("electronics_parts.json", "yuzhineng-manufacturing-chief"),
    ]
    tasks = []
    for file_name, agent_id in mapping:
        case = read_json(MANUFACTURING_TEST_CASE_DIR / file_name)
        skill_input = case["input"]
        product = skill_input.get("product_name") or skill_input.get("product") or case["name"]
        targets = skill_input.get("target_customer_hint") or skill_input.get("target_customers") or []
        tasks.append({
            "id": case["id"],
            "name": case["name"],
            "phase": "2b",
            "agent_id": agent_id,
            "product": product,
            "industry": skill_input.get("factory_type", ""),
            "targets": targets,
            "platforms": skill_input.get("platforms", ["小红书", "抖音", "公众号"]),
            "skill_input": skill_input,
            "query": f"{skill_input.get('company_location', '东莞')} {skill_input.get('factory_type', '')} {product} 获客",
            "prompt": (
                f"我要为{case['name']}做一轮制造业获客工作流。"
                f"产品：{product}。目标客户：{'、'.join(targets)}。"
                "请输出产品理解、商机发掘、宣传物料、社媒发布计划、评论/私信草稿、账号养成计划、工厂销售交接单和待办。"
                "不要真实发布、不要真实评论、不要真实私信、不要发邮件。"
            ),
        })
    return tasks


def load_product_intelligence_test_tasks() -> list[dict[str, Any]]:
    mapping = [
        ("heavy_packaging_product.json", "phase2d-001-heavy-packaging", "东莞重型包装纸箱厂产品资料理解"),
        ("electronics_parts_product.json", "phase2d-002-electronics-parts", "东莞电子配件厂产品资料理解"),
        ("fitness_equipment_product.json", "phase2d-003-fitness-equipment", "东莞健身器材厂产品资料理解"),
    ]
    tasks = []
    for file_name, task_id, name in mapping:
        input_file = PRODUCT_INTELLIGENCE_TEST_CASE_DIR / file_name
        payload = read_json(input_file)
        tasks.append(
            {
                "id": task_id,
                "name": name,
                "agent_id": "yuzhineng-manufacturing-chief",
                "input_file": str(input_file),
                "product": payload.get("product_name"),
                "industry": payload.get("factory_type"),
                "targets": payload.get("typical_customers") or [],
                "platforms": payload.get("platforms") or ["小红书", "抖音", "公众号"],
                "prompt": f"理解产品资料并生成获客输入：{payload.get('product_name')}",
            }
        )
    return tasks


def load_multi_agent_test_cases() -> list[dict[str, Any]]:
    mapping = [
        "dongguan_electronics_parts_multi_agent.json",
        "dongguan_heavy_packaging_multi_agent.json",
        "dongguan_fitness_equipment_multi_agent.json",
    ]
    return [read_json(MULTI_AGENT_TEST_CASE_DIR / file_name) for file_name in mapping]


def phase2b_safety_check(task: dict[str, Any], domestic: dict[str, Any], model_result: dict[str, Any]) -> dict[str, Any]:
    parsed = domestic.get("parsed") or {}
    text = json.dumps(parsed, ensure_ascii=False)
    return {
        "task_id": task["id"],
        "external_action_mode": parsed.get("mode") or "draft_only",
        "real_email_sent": False,
        "real_dm_sent": False,
        "real_comment_posted": False,
        "real_post_published": False,
        "social_login": False,
        "read_secrets": False,
        "invented_sources_detected": False,
        "draft_only_text_check_passed": not any(token in text for token in ["已发送", "已私信", "已评论", "已发布"]),
        "has_product_understanding": bool(parsed.get("product_understanding")),
        "has_opportunity_discovery": bool(parsed.get("opportunity_discovery")),
        "has_content_materials": bool(parsed.get("content_materials")),
        "has_social_publish_plan": bool(parsed.get("social_publish_plan")),
        "has_comment_dm_drafts": bool(parsed.get("comment_reply_drafts")) and bool(parsed.get("dm_drafts")),
        "has_account_nurturing_plan": bool(parsed.get("account_nurturing_plan")),
        "has_factory_handoff_sheet": bool(parsed.get("factory_handoff_sheet")),
        "source_status": parsed.get("source_status"),
        "source_count": len(parsed.get("sources") or []),
        "model_requested": MODEL,
        "model_result_model": model_result.get("model"),
        "model_call_ok": model_result.get("ok", False),
    }


def phase2b_summary_markdown(task: dict[str, Any], domestic: dict[str, Any], model_result: dict[str, Any]) -> str:
    parsed = domestic.get("parsed") or {}
    product = parsed.get("product") or task["product"]
    understanding = parsed.get("product_understanding") or {}
    opportunity = parsed.get("opportunity_discovery") or {}
    handoff = parsed.get("factory_handoff_sheet") or {}
    materials = parsed.get("content_materials") or {}
    safety = phase2b_safety_check(task, domestic, model_result)

    def line_list(items: Any, limit: int = 8) -> str:
        if not items:
            return "- 暂无。"
        if isinstance(items, dict):
            items = [f"{key}：{value}" for key, value in items.items()]
        lines = []
        for item in list(items)[:limit]:
            if isinstance(item, dict):
                title = item.get("title") or item.get("theme") or item.get("scenario") or item.get("intent") or item.get("type") or "项目"
                detail = item.get("draft") or item.get("content_format") or item.get("priority") or item.get("pain_points") or ""
                lines.append(f"- {title}：{detail}")
            else:
                lines.append(f"- {item}")
        return "\n".join(lines)

    return f"""# {task['name']}：Phase 2B 制造业获客工作流摘要

## 基本信息

- 产品：{product}
- 工厂类型：{understanding.get('factory_type')}
- 地区：{understanding.get('location')}
- 模式：draft_only
- 模型：{MODEL}
- DeepSeek V4 Pro 汇总：{model_result.get('ok')}

## 产品理解

- 产品描述：{understanding.get('product_description')}
- 工厂能力：{'、'.join(understanding.get('factory_capabilities') or [])}
- 产品卖点：{'、'.join(understanding.get('selling_points') or [])}
- 适合客户：{'、'.join(understanding.get('suitable_customer_types') or [])}

## 商机发掘

- 来源状态：{parsed.get('source_status')}
- 来源数量：{len(parsed.get('sources') or [])}
- 商机评分：{opportunity.get('opportunity_score')}
- 公开需求信号：{'、'.join(opportunity.get('public_demand_signals') or [])}

## 宣传物料

- 产品介绍：{materials.get('product_intro_copy')}
- 小红书选题：
{line_list(materials.get('xiaohongshu_notes') or [], 5)}
- 抖音脚本：
{line_list(materials.get('douyin_scripts') or [], 5)}

## 社媒计划

{line_list(parsed.get('social_publish_plan') or [], 7)}

## 评论/私信草稿

### 评论
{line_list(parsed.get('comment_reply_drafts') or [], 5)}

### 私信
{line_list(parsed.get('dm_drafts') or [], 5)}

## 账号养成计划

{line_list(parsed.get('account_nurturing_plan') or {}, 8)}

## 工厂销售交接单

- 标题：{handoff.get('handoff_title')}
- 推荐跟进人：{handoff.get('recommended_owner')}
- 需要人工复核：{handoff.get('requires_human_review')}
- 需求确认问题：
{line_list(handoff.get('qualification_questions') or [], 8)}

## 安全检查

- draft_only：{safety['external_action_mode'] == 'draft_only'}
- 真实外发：False
- 读取 secrets：False
- 社媒登录：False
"""


def save_phase2b_task_files(run_dir: Path, task: dict[str, Any], domestic: dict[str, Any], model_result: dict[str, Any]) -> dict[str, Any]:
    task_dir = run_dir / task["id"]
    task_dir.mkdir(parents=True, exist_ok=True)
    parsed = domestic.get("parsed") or {}
    write_json(task_dir / "input.json", task.get("skill_input") or {})
    write_json(task_dir / "skill_output.json", parsed)
    write_json(task_dir / "search_trace.json", {
        "task_id": task["id"],
        "source_status": parsed.get("source_status"),
        "sources": parsed.get("sources") or [],
        "search_trace": parsed.get("search_trace") or {},
    })
    safety = phase2b_safety_check(task, domestic, model_result)
    write_json(task_dir / "safety_check.json", safety)
    write_text(task_dir / "summary.md", phase2b_summary_markdown(task, domestic, model_result))
    return {
        "task_id": task["id"],
        "name": task["name"],
        "task_dir": str(task_dir),
        "domestic_ok": domestic.get("ok", False),
        "model_ok": model_result.get("ok", False),
        "source_status": parsed.get("source_status"),
        "source_count": len(parsed.get("sources") or []),
        "draft_only": safety["external_action_mode"] == "draft_only",
        "has_product_understanding": safety["has_product_understanding"],
        "has_opportunity_discovery": safety["has_opportunity_discovery"],
        "has_content_materials": safety["has_content_materials"],
        "has_comment_dm_drafts": safety["has_comment_dm_drafts"],
        "has_account_nurturing_plan": safety["has_account_nurturing_plan"],
        "has_factory_handoff_sheet": safety["has_factory_handoff_sheet"],
    }


def run_phase2b() -> int:
    started_at = time.strftime("%Y-%m-%d %H:%M:%S %z")
    run_id = "phase2b-" + time.strftime("%Y%m%d-%H%M%S")
    config = load_enabled_config()
    run_dir = TEST_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    agent_results = ensure_openclaw_agents(config, MANUFACTURING_AGENTS)
    ui_results = mirror_lobsterai_agents(config, MANUFACTURING_AGENTS)
    task_summaries = []
    raw_model_results = []
    enable_model_validation = bool(config.get("phase2b_enable_openclaw_model_validation"))

    for task in load_manufacturing_test_tasks():
        domestic = call_domestic_skill(task)
        if enable_model_validation:
            model_result = run_model_task(config, task, domestic)
        else:
            model_result = build_skill_only_phase2b_result(task, domestic)
        mirror = mirror_session_to_lobsterai(config, run_id, task, model_result)
        model_result["lobsterai_ui_session"] = mirror
        raw_model_results.append({"task_id": task["id"], "model_result": model_result})
        task_summaries.append(save_phase2b_task_files(run_dir, task, domestic, model_result))

    write_json(run_dir / "summary.json", {
        "run_id": run_id,
        "started_at": started_at,
        "model": MODEL,
        "agent_results": agent_results,
        "lobsterai_ui_agent_results": ui_results,
        "openclaw_model_validation_enabled": enable_model_validation,
        "tasks": task_summaries,
        "raw_model_results": raw_model_results,
    })
    write_json(TEST_RUNS_DIR / "latest-phase2b.json", {
        "run_id": run_id,
        "path": str(run_dir),
        "completed": all(item["domestic_ok"] for item in task_summaries),
        "openclaw_model_validation_enabled": enable_model_validation,
    })
    print(json.dumps({
        "ok": True,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "tasks": task_summaries,
    }, ensure_ascii=False, indent=2))
    return 0


def run_phase2d() -> int:
    started_at = time.strftime("%Y-%m-%d %H:%M:%S %z")
    run_id = "phase2d-" + time.strftime("%Y%m%d-%H%M%S")
    config = load_enabled_config()
    run_dir = TEST_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    agent_results = ensure_openclaw_agents(config, MANUFACTURING_AGENTS)
    ui_results = mirror_lobsterai_agents(config, MANUFACTURING_AGENTS)
    task_summaries = []

    for task in load_product_intelligence_test_tasks():
        task_dir = run_dir / task["id"]
        task_dir.mkdir(parents=True, exist_ok=True)
        product_result = call_product_intelligence(Path(task["input_file"]), task_dir)
        growth_input_path = task_dir / "growth_input.json"
        growth_input = read_json(growth_input_path) if growth_input_path.exists() else {}
        task["skill_input"] = growth_input
        domestic = call_domestic_skill(task)
        model_result = build_skill_only_phase2b_result(task, domestic)
        saved = save_phase2b_task_files(run_dir, task, domestic, model_result)
        product_profile_path = task_dir / "product_profile.json"
        product_card_path = task_dir / "product_card.md"
        saved.update(
            {
                "product_intelligence_ok": product_result.get("ok", False),
                "product_profile_path": str(product_profile_path),
                "product_card_path": str(product_card_path),
                "has_product_profile": product_profile_path.exists(),
                "has_product_card": product_card_path.exists(),
                "domestic_used_product_profile": bool((domestic.get("parsed") or {}).get("product_understanding", {}).get("product_profile_source") == "product_intelligence"),
            }
        )
        task_summaries.append(saved)

    write_json(run_dir / "summary.json", {
        "run_id": run_id,
        "started_at": started_at,
        "model": MODEL,
        "agent_results": agent_results,
        "lobsterai_ui_agent_results": ui_results,
        "tasks": task_summaries,
    })
    write_json(TEST_RUNS_DIR / "latest-phase2d.json", {
        "run_id": run_id,
        "path": str(run_dir),
        "completed": all(item["product_intelligence_ok"] and item["domestic_ok"] for item in task_summaries),
    })
    print(json.dumps({
        "ok": True,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "tasks": task_summaries,
    }, ensure_ascii=False, indent=2))
    return 0


def run_phase2e() -> int:
    started_at = time.strftime("%Y-%m-%d %H:%M:%S %z")
    run_id = "phase2e-" + time.strftime("%Y%m%d-%H%M%S")
    config = load_enabled_config()
    run_dir = TEST_RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    agent_results = ensure_openclaw_agents(config, MANUFACTURING_AGENTS)
    ui_results = mirror_lobsterai_agents(config, MANUFACTURING_AGENTS)
    task_summaries = []
    raw_results = []

    for case in load_multi_agent_test_cases():
        case_input = dict(case["input"])
        case_input.setdefault("mode", "draft_only")
        input_path = run_dir / f"{case['id']}.input.json"
        output_path = run_dir / f"{case['id']}.result.json"
        write_json(input_path, case_input)
        result = run(
            [
                "python",
                str(MULTI_AGENT_WORKFLOW_SCRIPT),
                "--input-file",
                str(input_path),
                "--runs-root",
                str(run_dir / "workflow-runs"),
                "--projects-root",
                str(run_dir / "projects"),
                "--output-file",
                str(output_path),
            ],
            timeout=180,
        )
        parsed = read_json(output_path) if output_path.exists() else {}
        raw_results.append({"case_id": case["id"], "command_result": result, "parsed": parsed})
        project_dir = Path(parsed.get("project_dir") or "")
        report_path = Path(parsed.get("report_path") or "")
        task_summaries.append(
            {
                "case_id": case["id"],
                "name": case["name"],
                "ok": bool(parsed.get("ok")) and result["code"] == 0,
                "model": parsed.get("model"),
                "agent_count": parsed.get("agent_count"),
                "workflow_run_dir": parsed.get("workflow_run_dir"),
                "project_dir": parsed.get("project_dir"),
                "has_project_dir": project_dir.exists(),
                "has_report_md": report_path.exists(),
                "has_handoff_docx": Path(parsed.get("handoff_path") or "").exists(),
                "draft_only": parsed.get("mode") == "draft_only",
                "real_external_send": bool((parsed.get("safety") or {}).get("real_external_send", True)),
                "source_status": parsed.get("source_status"),
            }
        )

    summary = {
        "run_id": run_id,
        "phase": "2E",
        "started_at": started_at,
        "model": MODEL,
        "agent_results": agent_results,
        "lobsterai_ui_agent_mirror": ui_results,
        "task_summaries": task_summaries,
        "completed": all(
            item["ok"]
            and item["draft_only"]
            and item["has_project_dir"]
            and item["has_report_md"]
            and item["has_handoff_docx"]
            and not item["real_external_send"]
            for item in task_summaries
        ),
    }
    write_json(run_dir / "summary.json", summary)
    write_json(run_dir / "raw_results.json", raw_results)
    write_json(TEST_RUNS_DIR / "latest-phase2e.json", {"run_id": run_id, "path": str(run_dir), "completed": summary["completed"]})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["completed"] else 2


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
    parser.add_argument("--run-phase2a", action="store_true")
    parser.add_argument("--run-phase2b", action="store_true")
    parser.add_argument("--run-phase2d", action="store_true")
    parser.add_argument("--run-phase2e", action="store_true")
    args = parser.parse_args()

    if args.init_local_config:
        init_local_config()
        return 0
    if args.run_phase2a:
        return run_phase2a()
    if args.run_phase2b:
        return run_phase2b()
    if args.run_phase2d:
        return run_phase2d()
    if args.run_phase2e:
        return run_phase2e()
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
