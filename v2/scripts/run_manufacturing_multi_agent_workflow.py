from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\OpenClaw")
V2 = ROOT / "v2"
DEFAULT_RUNS_ROOT = V2 / "data" / "workflow-runs"
DEFAULT_PROJECTS_ROOT = V2 / "projects"
DEFAULT_MODEL = "deepseek/deepseek-v4-pro"
WORKFLOW_PATH = V2 / "workflows" / "dongguan_manufacturing_growth" / "multi_agent_workflow.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PRODUCT_INTELLIGENCE = load_module(
    "phase2e_product_intelligence",
    V2 / "skills" / "product_intelligence" / "product_intelligence.py",
)
sys.path.insert(0, str(V2 / "skills" / "domestic_signal_growth"))
DOMESTIC_SIGNAL_GROWTH = load_module(
    "phase2e_domestic_signal_growth",
    V2 / "skills" / "domestic_signal_growth" / "domestic_signal_growth.py",
)
ARCHIVE = load_module(
    "phase2e_archive_manufacturing_growth_result",
    V2 / "scripts" / "archive_manufacturing_growth_result.py",
)


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def safe_slug(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "manufacturing-multi-agent"


def created_id(created_at: str | None = None) -> str:
    if created_at:
        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})", created_at)
        if match:
            y, m, d, hh, mm, ss = match.groups()
            return f"{y}{m}{d}-{hh}{mm}{ss}"
    return time.strftime("%Y%m%d-%H%M%S")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S+0800")


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def normalize_input(payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload or {})
    if isinstance(payload.get("input"), dict):
        payload = dict(payload["input"])
    product = payload.get("product_name") or payload.get("product") or "制造业产品"
    factory_type = payload.get("factory_type") or payload.get("industry") or "制造业工厂"
    targets = payload.get("target_customer_hint") or payload.get("target_customers") or payload.get("targets") or []
    normalized = {
        "company_location": payload.get("company_location") or payload.get("city") or "东莞",
        "factory_type": factory_type,
        "industry": factory_type,
        "product_name": product,
        "product": product,
        "product_description": payload.get("product_description") or "",
        "materials": normalize_list(payload.get("materials")),
        "specifications": normalize_list(payload.get("specifications") or payload.get("main_specs")),
        "factory_capabilities": normalize_list(payload.get("factory_capabilities")),
        "certifications": normalize_list(payload.get("certifications")),
        "delivery_cycle": payload.get("delivery_cycle") or payload.get("delivery_notes") or "",
        "price_range": payload.get("price_range") or "",
        "typical_customers": normalize_list(payload.get("typical_customers") or targets),
        "target_customers": normalize_list(targets),
        "target_customer_hint": normalize_list(targets),
        "platforms": normalize_list(payload.get("platforms")) or ["小红书", "抖音", "公众号"],
        "mode": "draft_only",
        "search_required": bool(payload.get("search_required", True)),
    }
    if isinstance(payload.get("manual_seed_urls"), list):
        normalized["manual_seed_urls"] = payload["manual_seed_urls"]
    if payload.get("search_provider"):
        normalized["search_provider"] = payload["search_provider"]
    return normalized


def load_workflow_config() -> dict[str, Any]:
    return read_json(WORKFLOW_PATH)


def build_plan(input_data: dict[str, Any], run_id: str, created_at: str) -> dict[str, Any]:
    workflow = load_workflow_config()
    return {
        "workflow_run_id": run_id,
        "workflow_id": workflow["id"],
        "title": f"{input_data['product_name']} 多 Agent 获客工作流",
        "user_goal": f"为{input_data['company_location']}{input_data['factory_type']}推广{input_data['product_name']}，目标客户：{'、'.join(input_data['target_customer_hint'])}",
        "model": DEFAULT_MODEL,
        "mode": "draft_only",
        "external_action_mode": "draft_only",
        "approval_required": True,
        "created_at": created_at,
        "agents": workflow["agents"],
        "steps": workflow["steps"],
        "notes_for_user": "本轮只生成获客方案、宣传物料、评论/私信草稿、销售交接单和待办，不真实发布、不评论、不私信、不发邮件。",
    }


def build_agent_tasks(plan: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    step_by_agent = {
        "yuzhineng-manufacturing-chief": "总控拆解与最终汇总",
        "yuzhineng-product-analyst": "产品资料理解",
        "yuzhineng-opportunity-researcher": "商机发掘与公开来源整理",
        "yuzhineng-content-producer": "宣传物料生成",
        "yuzhineng-social-operator": "社媒运营草稿和账号养成",
        "yuzhineng-factory-handoff": "工厂销售交接",
        "yuzhineng-safety-reviewer": "风控审核",
        "yuzhineng-archive-agent": "项目归档",
    }
    for index, agent in enumerate(plan["agents"], start=1):
        tasks.append(
            {
                "order": index,
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "assignment": step_by_agent.get(agent["id"], agent.get("role", "")),
                "expected_output": agent.get("role", ""),
                "status": "completed",
                "mode": "draft_only",
            }
        )
    return tasks


def list_lines(items: Any, limit: int = 8) -> str:
    values = items if isinstance(items, list) else ([] if items is None else [items])
    if not values:
        return "- 暂无。"
    lines = []
    for item in values[:limit]:
        if isinstance(item, dict):
            title = item.get("title") or item.get("theme") or item.get("type") or item.get("segment") or item.get("scenario") or item.get("intent") or item.get("day") or "项目"
            detail = item.get("draft") or item.get("why_fit") or item.get("pain_points") or item.get("content_format") or item.get("priority") or ""
            if isinstance(detail, list):
                detail = "、".join(str(part) for part in detail)
            lines.append(f"- {title}" + (f"：{detail}" if detail else ""))
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def build_content_agent_output(opportunity_output: dict[str, Any]) -> dict[str, Any]:
    materials = opportunity_output.get("content_materials") or {}
    return {
        "agent_id": "yuzhineng-content-producer",
        "agent_name": "宣传物料 Agent",
        "mode": "draft_only",
        "xiaohongshu_notes": materials.get("xiaohongshu_notes") or [],
        "douyin_scripts": materials.get("douyin_scripts") or [],
        "wechat_article_outline": materials.get("wechat_article_outline") or [],
        "product_intro_copy": materials.get("product_intro_copy") or "",
        "sales_talk_track": materials.get("sales_talk_track") or [],
        "status": "completed",
    }


def build_social_agent_output(opportunity_output: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": "yuzhineng-social-operator",
        "agent_name": "社媒运营 Agent",
        "mode": "draft_only",
        "social_publish_plan": opportunity_output.get("social_publish_plan") or [],
        "comment_reply_drafts": opportunity_output.get("comment_reply_drafts") or [],
        "dm_drafts": opportunity_output.get("dm_drafts") or [],
        "account_nurturing_plan": opportunity_output.get("account_nurturing_plan") or {},
        "external_actions": "draft_only_only",
        "status": "completed",
    }


def build_factory_agent_output(opportunity_output: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": "yuzhineng-factory-handoff",
        "agent_name": "工厂对接 Agent",
        "mode": "draft_only",
        "factory_handoff_sheet": opportunity_output.get("factory_handoff_sheet") or {},
        "todos": opportunity_output.get("todos") or [],
        "next_steps": opportunity_output.get("next_steps") or [],
        "status": "completed",
    }


def build_safety_agent_output(
    input_data: dict[str, Any],
    opportunity_output: dict[str, Any],
    content_output: dict[str, Any],
    social_output: dict[str, Any],
    factory_output: dict[str, Any],
) -> dict[str, Any]:
    combined_text = json.dumps(
        {
            "input": input_data,
            "opportunity": opportunity_output,
            "content": content_output,
            "social": social_output,
            "factory": factory_output,
        },
        ensure_ascii=False,
    )
    risky_claims = [token for token in ["已发送", "已私信", "已评论", "已发布", "已发邮件"] if token in combined_text]
    return {
        "agent_id": "yuzhineng-safety-reviewer",
        "agent_name": "风控审核 Agent",
        "external_action_mode": "draft_only",
        "approval_required": True,
        "real_external_send": False,
        "real_email_sent": False,
        "real_dm_sent": False,
        "real_comment_posted": False,
        "real_post_published": False,
        "read_secrets": False,
        "invented_sources": False,
        "risky_claims": risky_claims,
        "risk_notes": [
            "所有发布、评论、私信、邮件仅为草稿或人工待办。",
            "报价、交期、认证、客户案例和公开来源必须人工复核。",
            *normalize_list(opportunity_output.get("risk_notes")),
        ],
        "status": "passed" if not risky_claims else "needs_review",
    }


def build_agent_room_messages(plan: dict[str, Any], source_status: str) -> list[dict[str, Any]]:
    messages = []
    for agent in plan["agents"]:
        messages.append(
            {
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "message": f"我已完成自己的分工：{agent['role']} 当前模式为 draft_only。",
                "visible_to_user": True,
            }
        )
    messages.append(
        {
            "agent_id": "yuzhineng-manufacturing-chief",
            "agent_name": "宇智能制造业获客总控 Agent",
            "message": f"本轮多 Agent 协作已汇总完成。公开来源状态：{source_status}。所有外部动作仍需人工审批。",
            "visible_to_user": True,
        }
    )
    return messages


def build_final_report(
    plan: dict[str, Any],
    product_output: dict[str, Any],
    opportunity_output: dict[str, Any],
    content_output: dict[str, Any],
    social_output: dict[str, Any],
    factory_output: dict[str, Any],
    safety_output: dict[str, Any],
    archive_output: dict[str, Any] | None,
) -> str:
    profile = product_output.get("product_profile") or {}
    opportunity = opportunity_output.get("opportunity_discovery") or {}
    sources = opportunity_output.get("sources") or opportunity_output.get("public_sources") or []
    handoff = factory_output.get("factory_handoff_sheet") or {}
    archive_output = archive_output or {}
    agents_text = "\n".join(
        f"- {agent['name']}：{agent['role']}" for agent in plan.get("agents", [])
    )
    return f"""# 宇智能制造业获客工作流结果

## 1. 总控 Agent 任务拆解

- 用户目标：{plan['user_goal']}
- 当前模式：draft_only
- 使用模型：{plan['model']}
- 分配给哪些 Agent：
{agents_text}
- 哪些动作需要人工审批：发布、评论、私信、邮件、报价、交期、认证、客户案例和外部来源引用。
- 总控结论：先用产品理解和公开信号生成获客草稿，再由人工确认素材与外部动作。

## 2. 产品理解 Agent 输出

- 产品卡：{profile.get('product_name') or '待补充'}
- 卖点：
{list_lines(product_output.get('selling_points'))}
- 应用场景：
{list_lines(product_output.get('application_scenarios'))}
- 适合客户：
{list_lines(product_output.get('suitable_customer_segments'))}
- 缺失信息：
{list_lines(product_output.get('missing_information'))}

## 3. 商机发掘 Agent 输出

- 客户方向：
{list_lines(opportunity_output.get('target_customer_segments') or opportunity_output.get('target_customer_types'))}
- 公开来源状态：{opportunity_output.get('source_status') or 'unknown'}
- 公开来源：
{list_lines([{'title': item.get('title'), 'draft': item.get('url')} for item in sources])}
- 采购信号：
{list_lines(opportunity.get('public_demand_signals'))}
- 商机评分：{opportunity.get('opportunity_score') or 'unknown'}

## 4. 宣传物料 Agent 输出

- 小红书草稿：
{list_lines(content_output.get('xiaohongshu_notes'), 10)}
- 抖音脚本：
{list_lines(content_output.get('douyin_scripts'), 10)}
- 公众号大纲：
{list_lines(content_output.get('wechat_article_outline'), 10)}
- 产品介绍：{content_output.get('product_intro_copy') or '待补充'}
- 销售话术：
{list_lines(content_output.get('sales_talk_track'))}

## 5. 社媒运营 Agent 输出

- 7 天内容计划：
{list_lines(social_output.get('social_publish_plan'), 10)}
- 评论回复草稿：
{list_lines(social_output.get('comment_reply_drafts'))}
- 私信草稿：
{list_lines(social_output.get('dm_drafts'))}
- 账号养成计划：
{list_lines((social_output.get('account_nurturing_plan') or {}).get('thirty_day_content_directions'))}

## 6. 工厂对接 Agent 输出

- 销售交接单摘要：{handoff.get('handoff_title') or '待生成'}
- 跟进 SOP：
{list_lines(handoff.get('handoff_talk_track'))}
- 待办：
{list_lines(factory_output.get('todos'))}

## 7. 风控审核 Agent 输出

- 风险提醒：
{list_lines(safety_output.get('risk_notes'))}
- 是否存在真实外发：否
- 是否需要人工审批：是
- 风控状态：{safety_output.get('status')}

## 8. 归档 Agent 输出

- 项目目录：{archive_output.get('project_dir') or '待归档'}
- report.md：{archive_output.get('report_path') or '待归档'}
- handoff.docx：{archive_output.get('handoff_path') or '待归档'}
- product_card.md：{(Path(archive_output.get('project_dir', '')) / 'product_card.md') if archive_output.get('project_dir') else '待归档'}
- todos.json：{(Path(archive_output.get('project_dir', '')) / 'todos.json') if archive_output.get('project_dir') else '待归档'}
- index.html 链接：{archive_output.get('projects_index_html') or '待归档'}

## draft_only 声明

本轮为宇智能多 Agent 协作草稿，不真实发布、评论、私信或发邮件。所有对外动作必须人工复核后在外部平台手动处理。
"""


def build_trace(
    plan: dict[str, Any],
    agent_tasks: list[dict[str, Any]],
    archive_output: dict[str, Any],
) -> str:
    lines = [
        "# Phase 2E 多 Agent 工作流轨迹",
        "",
        f"- workflow_run_id：{plan['workflow_run_id']}",
        f"- model：{plan['model']}",
        f"- mode：{plan['mode']}",
        "",
        "## Agent 执行顺序",
    ]
    for task in agent_tasks:
        lines.append(f"- {task['order']}. {task['agent_name']}：{task['assignment']}，状态：{task['status']}")
    lines.extend(
        [
            "",
            "## 归档结果",
            f"- 项目目录：{archive_output.get('project_dir')}",
            f"- 项目索引：{archive_output.get('projects_index_html')}",
            "",
            "## 安全边界",
            "- 未真实发布。",
            "- 未真实评论。",
            "- 未真实私信。",
            "- 未发邮件。",
            "- 未读取 secrets。",
        ]
    )
    return "\n".join(lines) + "\n"


def build_skill_output(
    product_output: dict[str, Any],
    opportunity_output: dict[str, Any],
    plan: dict[str, Any],
    agent_tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    skill_output = dict(opportunity_output)
    skill_output["product_intelligence_output"] = product_output
    skill_output["multi_agent_workflow"] = {
        "workflow_run_id": plan["workflow_run_id"],
        "model": plan["model"],
        "agents": plan["agents"],
        "agent_tasks": agent_tasks,
        "external_action_mode": "draft_only",
    }
    skill_output["mode"] = "draft_only"
    return skill_output


def run_workflow(
    payload: dict[str, Any],
    *,
    runs_root: str | Path = DEFAULT_RUNS_ROOT,
    projects_root: str | Path = DEFAULT_PROJECTS_ROOT,
    created_at: str | None = None,
) -> dict[str, Any]:
    input_data = normalize_input(payload)
    created_at = created_at or now_iso()
    run_id = f"{created_id(created_at)}-{safe_slug(input_data['product_name'])}-multi-agent"
    run_dir = Path(runs_root) / run_id
    if run_dir.exists():
        run_dir = Path(runs_root) / f"{run_id}-{time.strftime('%H%M%S')}"
        run_id = run_dir.name
    run_dir.mkdir(parents=True, exist_ok=False)

    plan = build_plan(input_data, run_id, created_at)
    agent_tasks = build_agent_tasks(plan)
    product_output = PRODUCT_INTELLIGENCE.analyze_product_materials(input_data)
    growth_input = dict(product_output.get("next_growth_inputs") or {})
    growth_input.update(
        {
            "product_profile": product_output.get("product_profile"),
            "product_intelligence_output": product_output,
            "target_customers": input_data["target_customer_hint"],
            "target_customer_hint": input_data["target_customer_hint"],
            "platforms": input_data["platforms"],
            "search_required": input_data["search_required"],
            "mode": "draft_only",
        }
    )
    if "manual_seed_urls" in input_data:
        growth_input["manual_seed_urls"] = input_data["manual_seed_urls"]
        growth_input["search_provider"] = input_data.get("search_provider", "manual_seed_urls")
    elif "search_provider" in input_data:
        growth_input["search_provider"] = input_data["search_provider"]

    opportunity_output = DOMESTIC_SIGNAL_GROWTH.generate_signal_report(growth_input)
    content_output = build_content_agent_output(opportunity_output)
    social_output = build_social_agent_output(opportunity_output)
    factory_output = build_factory_agent_output(opportunity_output)
    safety_output = build_safety_agent_output(input_data, opportunity_output, content_output, social_output, factory_output)
    room_messages = build_agent_room_messages(plan, opportunity_output.get("source_status") or "unknown")

    write_json(run_dir / "input.json", input_data)
    write_json(run_dir / "plan.json", plan)
    write_json(run_dir / "agent_tasks.json", agent_tasks)
    write_json(run_dir / "agent_room_messages.json", room_messages)
    write_json(run_dir / "product_agent_output.json", product_output)
    write_json(run_dir / "opportunity_agent_output.json", opportunity_output)
    write_json(run_dir / "content_agent_output.json", content_output)
    write_json(run_dir / "social_agent_output.json", social_output)
    write_json(run_dir / "factory_handoff_agent_output.json", factory_output)
    write_json(run_dir / "safety_agent_output.json", safety_output)

    skill_output = build_skill_output(product_output, opportunity_output, plan, agent_tasks)
    archive_input_dir = run_dir / "archive_input"
    write_json(archive_input_dir / "input.json", input_data)
    write_json(archive_input_dir / "skill_output.json", skill_output)
    write_json(archive_input_dir / "sources.json", opportunity_output.get("sources") or opportunity_output.get("public_sources") or [])
    write_json(archive_input_dir / "search_trace.json", opportunity_output.get("search_trace") or {})
    write_json(archive_input_dir / "safety_check.json", safety_output)

    preliminary_report = build_final_report(
        plan,
        product_output,
        opportunity_output,
        content_output,
        social_output,
        factory_output,
        safety_output,
        None,
    )
    final_report_path = run_dir / "final_report.md"
    write_text(final_report_path, preliminary_report)
    write_text(archive_input_dir / "summary.md", preliminary_report)

    archive_output = ARCHIVE.archive_task_output(
        archive_input_dir,
        projects_root=projects_root,
        project_slug=f"{input_data['factory_type']}-{input_data['product_name']}-multi-agent",
        project_name=f"{input_data['factory_type']}-{input_data['product_name']} 多 Agent 获客工作流",
        created_at=created_at,
        report_source=final_report_path,
    )
    write_json(run_dir / "archive_agent_output.json", archive_output)

    final_report = build_final_report(
        plan,
        product_output,
        opportunity_output,
        content_output,
        social_output,
        factory_output,
        safety_output,
        archive_output,
    )
    write_text(final_report_path, final_report)
    project_report_path = Path(archive_output["report_path"])
    write_text(project_report_path, final_report)
    write_text(run_dir / "trace.md", build_trace(plan, agent_tasks, archive_output))

    return {
        "ok": True,
        "workflow_run_id": run_id,
        "workflow_run_dir": str(run_dir),
        "project_dir": archive_output["project_dir"],
        "report_path": archive_output["report_path"],
        "handoff_path": archive_output["handoff_path"],
        "projects_index_html": archive_output["projects_index_html"],
        "model": DEFAULT_MODEL,
        "mode": "draft_only",
        "source_status": opportunity_output.get("source_status"),
        "agent_count": len(plan["agents"]),
        "safety": safety_output,
    }


def parse_text_task(text: str) -> dict[str, Any]:
    text = text.strip()
    if "电子" in text or "连接件" in text or "线束" in text:
        product = "电子连接件、线束、充电配件"
        factory = "电子配件厂"
        targets = ["电子厂", "品牌商", "跨境卖家", "维修渠道"]
    elif "包装" in text or "纸箱" in text:
        product = "重型包装纸箱、物流包装、出口包装"
        factory = "包装厂"
        targets = ["电商仓储", "制造工厂", "物流公司", "外贸企业"]
    elif "健身" in text or "哑铃" in text:
        product = "哑铃、力量训练器材、家用健身器材"
        factory = "健身器材厂"
        targets = ["健身房", "经销商", "跨境卖家", "团购客户"]
    else:
        product = text[:60] or "制造业产品"
        factory = "制造业工厂"
        targets = ["品牌商", "经销商", "跨境卖家"]
    return {
        "company_location": "东莞",
        "factory_type": factory,
        "product_name": product,
        "product_description": text,
        "target_customer_hint": targets,
        "platforms": ["小红书", "抖音", "公众号"],
        "mode": "draft_only",
        "search_required": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="宇智能制造业多 Agent 获客工作流执行器")
    parser.add_argument("--input-file", default="")
    parser.add_argument("--input-json", default="")
    parser.add_argument("--task", default="")
    parser.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--projects-root", default=str(DEFAULT_PROJECTS_ROOT))
    parser.add_argument("--created-at", default="")
    parser.add_argument("--output-file", default="")
    return parser.parse_args()


def read_input(args: argparse.Namespace) -> dict[str, Any]:
    if args.input_file:
        return read_json(Path(args.input_file))
    if args.input_json:
        return json.loads(args.input_json)
    if args.task:
        return parse_text_task(args.task)
    raise ValueError("需要提供 --input-file、--input-json 或 --task")


def main() -> int:
    args = parse_args()
    try:
        result = run_workflow(
            read_input(args),
            runs_root=args.runs_root,
            projects_root=args.projects_root,
            created_at=args.created_at or None,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output_file:
        write_text(Path(args.output_file), text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
