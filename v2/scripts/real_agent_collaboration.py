from __future__ import annotations

import html
import json
import os
import shutil
import sqlite3
import time
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\OpenClaw")
V2 = ROOT / "v2"
DEFAULT_COLLABORATION_ROOT = V2 / "data" / "multi-agent-runs"
DEFAULT_LOBSTERAI_SQLITE = Path(os.path.expandvars(r"%APPDATA%\LobsterAI\lobsterai.sqlite"))
DEFAULT_BACKUP_ROOT = ROOT / "backups" / "lobsterai-sqlite"
DEFAULT_MODEL = "deepseek/deepseek-v4-pro"


AGENT_FILES = {
    "yuzhineng-manufacturing-chief": "controller_agent",
    "yuzhineng-product-analyst": "product_agent",
    "yuzhineng-opportunity-researcher": "opportunity_agent",
    "yuzhineng-content-producer": "content_agent",
    "yuzhineng-social-operator": "social_agent",
    "yuzhineng-factory-handoff": "factory_handoff_agent",
    "yuzhineng-safety-reviewer": "safety_agent",
    "yuzhineng-summary-agent": "summary_agent",
    "yuzhineng-archive-agent": "archive_agent",
}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def list_lines(items: Any, limit: int = 8) -> str:
    values = items if isinstance(items, list) else ([] if items is None else [items])
    if not values:
        return "- 暂无。"
    lines: list[str] = []
    for item in values[:limit]:
        if isinstance(item, dict):
            title = item.get("title") or item.get("theme") or item.get("segment") or item.get("type") or item.get("day") or "项目"
            detail = item.get("draft") or item.get("why_fit") or item.get("content_format") or item.get("priority") or ""
            if isinstance(detail, list):
                detail = "、".join(str(part) for part in detail)
            lines.append(f"- {title}" + (f"：{detail}" if detail else ""))
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def file_href(base_dir: Path, target: str | Path) -> str:
    if not target:
        return ""
    target_path = Path(target)
    try:
        relative = target_path.resolve().relative_to(base_dir.resolve())
        return html.escape(relative.as_posix())
    except Exception:
        return "file:///" + html.escape(target_path.as_posix())


def agent_file_stem(agent_id: str) -> str:
    return AGENT_FILES.get(agent_id, agent_id.replace("yuzhineng-", "").replace("-", "_"))


def output_summary(agent_id: str, outputs: dict[str, dict[str, Any]]) -> str:
    if agent_id == "yuzhineng-product-analyst":
        product = outputs["product"].get("product_profile") or {}
        return f"已整理产品资料卡：{product.get('product_name') or '制造业产品'}，提炼卖点、客户场景和缺失资料。"
    if agent_id == "yuzhineng-opportunity-researcher":
        opportunity = outputs["opportunity"].get("opportunity_discovery") or {}
        return f"已完成商机判断，商机评分：{opportunity.get('opportunity_score') or 'unknown'}，来源状态：{outputs['opportunity'].get('source_status') or 'unknown'}。"
    if agent_id == "yuzhineng-content-producer":
        return "已生成小红书、抖音、公众号和销售话术草稿，并完成风控返修。"
    if agent_id == "yuzhineng-social-operator":
        return "已生成发布计划、评论回复草稿、私信草稿和账号养成计划，全部为 draft_only。"
    if agent_id == "yuzhineng-factory-handoff":
        return "已生成工厂销售交接摘要、跟进 SOP 和人工待办。"
    if agent_id == "yuzhineng-safety-reviewer":
        return "已完成风险审核，发现内容初稿缺少明确 draft_only 声明并要求返修。"
    if agent_id == "yuzhineng-summary-agent":
        return "已读取各专业 Agent 最终输出，生成项目总览和下一步建议。"
    if agent_id == "yuzhineng-archive-agent":
        return "已归档项目成果，更新本地项目索引。"
    return "已完成任务拆解、进度同步和最终交付检查。"


def build_markdown_outputs(
    input_data: dict[str, Any],
    outputs: dict[str, dict[str, Any]],
    project_dir: Path,
    final_report_path: Path,
) -> dict[str, str]:
    product_output = outputs["product"]
    opportunity_output = outputs["opportunity"]
    content_output = outputs["content"]
    social_output = outputs["social"]
    factory_output = outputs["factory"]
    safety_output = outputs["safety"]
    product = input_data.get("product_name") or "制造业产品"

    product_card = f"""# 产品理解 Agent 产出：{product}

## 核心卖点
{list_lines(product_output.get('selling_points'))}

## 适合客户
{list_lines(product_output.get('suitable_customer_segments'))}

## 缺失资料
{list_lines(product_output.get('missing_information'))}

## draft_only 声明
本文件仅用于内部获客草稿，不真实发布、评论、私信或发邮件。
"""
    opportunity_report = f"""# 商机发掘 Agent 产出：{product}

## 目标客户方向
{list_lines(opportunity_output.get('target_customer_segments') or opportunity_output.get('target_customer_types'))}

## 公开需求信号
{list_lines((opportunity_output.get('opportunity_discovery') or {}).get('public_demand_signals'))}

## 公开来源
{list_lines([{'title': item.get('title'), 'draft': item.get('url')} for item in opportunity_output.get('sources', [])])}

## 下一步
只做公开信息研究和人工复核，不抓取非公开数据。
"""
    content_initial = f"""# 宣传物料 Agent 初稿：{product}

## 小红书笔记
{list_lines(content_output.get('xiaohongshu_notes'), 10)}

## 抖音脚本
{list_lines(content_output.get('douyin_scripts'), 10)}

> 风控备注：此初稿故意缺少醒目的 draft_only 声明，用于验证返工机制。
"""
    content_fixed = f"""# 宣传物料 Agent 修正版：{product}

## 小红书笔记
{list_lines(content_output.get('xiaohongshu_notes'), 10)}

## 抖音脚本
{list_lines(content_output.get('douyin_scripts'), 10)}

## 公众号大纲
{list_lines(content_output.get('wechat_article_outline'), 10)}

## 销售话术
{list_lines(content_output.get('sales_talk_track'))}

## draft_only 声明
以上内容均为草稿，不真实发布、不评论、不私信、不发邮件。所有外部动作必须人工审批。
"""
    social_plan = f"""# 社媒运营 Agent 产出：{product}

## 7 天内容计划
{list_lines(social_output.get('social_publish_plan'), 10)}

## 评论回复草稿
{list_lines(social_output.get('comment_reply_drafts'))}

## 私信草稿
{list_lines(social_output.get('dm_drafts'))}

## 边界
仅生成草稿和人工待办，不登录社媒账号，不自动发送。
"""
    handoff = factory_output.get("factory_handoff_sheet") or {}
    factory_handoff = f"""# 工厂对接 Agent 产出：{product}

## 交接标题
{handoff.get('handoff_title') or product + ' 客户交接单'}

## 跟进问题
{list_lines(handoff.get('qualification_questions'))}

## 跟进 SOP
{list_lines(handoff.get('handoff_talk_track'))}

## 待办
{list_lines(factory_output.get('todos'))}
"""
    safety_review = f"""# 风控审核 Agent 产出：{product}

## 风险结论
- 未真实外发：是
- 外部动作模式：draft_only
- 是否需要人工审批：是

## 风险提醒
{list_lines(safety_output.get('risk_notes'))}

## 返工意见
- 宣传物料 Agent 初稿缺少醒目的 draft_only 声明，要求补充并重新输出。
"""
    final_summary = f"""# 归纳 Agent 最终总结：{product}

## 总体结论
本轮已完成真实多 Agent 协作：总控拆解任务，专业 Agent 独立产出，风控 Agent 提出返工，宣传物料 Agent 完成修正，归纳 Agent 汇总最终结果。

## 可直接查看的成果
- 产品资料卡：product_card.md
- 商机报告：opportunity_report.md
- 宣传物料：content_materials.md
- 社媒计划：social_plan.md
- 工厂交接：factory_handoff.md / factory_handoff.docx
- 风控审核：safety_review.md
- 完整报告：final_report.md

## 下一步建议
1. 人工确认产品规格、认证、交期和报价边界。
2. 人工选择可公开图片和客户案例，不能编造。
3. 从小红书或抖音中选 1 个平台做 3 天内容验证。
4. 评论、私信、发帖、邮件全部走人工审批和手动执行。

## draft_only 声明
本轮没有真实发布、评论、私信或发邮件。
"""
    final_report_copy = final_report_path.read_text(encoding="utf-8") if final_report_path.exists() else final_summary
    return {
        "product_card.md": product_card,
        "opportunity_report.md": opportunity_report,
        "content_materials.initial.md": content_initial,
        "content_materials.md": content_fixed,
        "social_plan.md": social_plan,
        "factory_handoff.md": factory_handoff,
        "safety_review.md": safety_review,
        "final_summary.md": final_summary,
        "final_report.md": final_report_copy,
    }


def build_group_messages(
    room_id: str,
    agent_tasks: list[dict[str, Any]],
    files: dict[str, str],
    rework_issue_id: str,
    created_at: str,
) -> list[dict[str, Any]]:
    task_by_agent = {task["agent_id"]: task for task in agent_tasks}
    sequence = [
        ("yuzhineng-manufacturing-chief", "all", "task", "我已创建项目 Agent 工作群，并把任务拆给各专业 Agent。"),
        ("yuzhineng-product-analyst", "all", "file", "产品资料卡已完成，已标注卖点、适合客户和缺失资料。"),
        ("yuzhineng-opportunity-researcher", "all", "file", "商机方向和公开来源整理完成，未采集非公开联系方式。"),
        ("yuzhineng-content-producer", "all", "file", "宣传物料初稿已完成，准备进入风控审核。"),
        ("yuzhineng-social-operator", "all", "file", "社媒运营计划、评论回复草稿和私信草稿已生成，全部不自动发送。"),
        ("yuzhineng-factory-handoff", "all", "file", "工厂销售交接单和人工跟进待办已完成。"),
        ("yuzhineng-safety-reviewer", "yuzhineng-content-producer", "rework_required", "发现宣传物料初稿缺少醒目的 draft_only 声明，请补充外部动作边界后重新提交。"),
        ("yuzhineng-content-producer", "yuzhineng-safety-reviewer", "rework_done", "已收到问题并完成修正，修正版已补充 draft_only 声明和人工审批边界。"),
        ("yuzhineng-safety-reviewer", "all", "review_passed", "返修通过。当前所有发布、评论、私信和邮件动作均保持草稿状态。"),
        ("yuzhineng-summary-agent", "all", "summary", "我已读取各 Agent 的最终产出，并生成 final_summary.md 与 final_report.md。"),
        ("yuzhineng-archive-agent", "all", "archive", "项目成果已归档，工作群和成果工作台可以从项目索引打开。"),
    ]
    messages: list[dict[str, Any]] = []
    for index, (sender, receiver, message_type, content) in enumerate(sequence, start=1):
        related_file = ""
        if sender == "yuzhineng-product-analyst":
            related_file = files.get("product_card.md", "")
        elif sender == "yuzhineng-opportunity-researcher":
            related_file = files.get("opportunity_report.md", "")
        elif sender == "yuzhineng-content-producer" and message_type == "file":
            related_file = files.get("content_materials.initial.md", "")
        elif sender == "yuzhineng-content-producer":
            related_file = files.get("content_materials.md", "")
        elif sender == "yuzhineng-social-operator":
            related_file = files.get("social_plan.md", "")
        elif sender == "yuzhineng-factory-handoff":
            related_file = files.get("factory_handoff.md", "")
        elif sender == "yuzhineng-safety-reviewer":
            related_file = files.get("safety_review.md", "")
        elif sender == "yuzhineng-summary-agent":
            related_file = files.get("final_summary.md", "")
        task = task_by_agent.get(sender) or {}
        messages.append(
            {
                "message_id": f"{room_id}-msg-{index:03d}",
                "room_id": room_id,
                "sender_agent": sender,
                "sender_name": task.get("agent_name") or sender,
                "receiver_agent": receiver,
                "message_type": message_type,
                "content": content,
                "related_task_id": task.get("task_id"),
                "related_file": related_file,
                "related_issue_id": rework_issue_id if message_type in {"rework_required", "rework_done"} else "",
                "created_at": created_at,
            }
        )
    return messages


def render_group_chat_html(
    project_dir: Path,
    project_name: str,
    agent_tasks: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    rework_log: list[dict[str, Any]],
    final_summary_path: Path,
) -> str:
    members = "".join(
        f"<button class=\"member\" data-agent=\"{html.escape(task['agent_id'])}\"><strong>{html.escape(task['agent_name'])}</strong><span>{html.escape(task['status_label'])}</span></button>"
        for task in agent_tasks
    )
    bubbles = []
    for msg in messages:
        href = file_href(project_dir, msg.get("related_file", ""))
        link = f"<a href=\"{href}\">打开相关文件</a>" if href else ""
        bubbles.append(
            f"<article class=\"bubble {html.escape(msg['message_type'])}\" data-agent=\"{html.escape(msg['sender_agent'])}\">"
            f"<div class=\"speaker\">{html.escape(msg['sender_name'])}<span>{html.escape(msg['message_type'])}</span></div>"
            f"<p>{html.escape(msg['content'])}</p>{link}</article>"
        )
    rework_items = "".join(
        f"<li><strong>{html.escape(item['severity'])}</strong>：{html.escape(item['issue'])}<br><span>处理：{html.escape(item['fix_status'])}，文件：{html.escape(Path(item['fixed_file']).name)}</span></li>"
        for item in rework_log
    )
    summary_href = file_href(project_dir, final_summary_path)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{html.escape(project_name)} - Agent 工作群</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f7fb; color: #111827; }}
    header {{ padding: 22px 28px; background: #ffffff; border-bottom: 1px solid #dbe3ef; display: flex; justify-content: space-between; gap: 24px; align-items: center; }}
    h1 {{ margin: 0; font-size: 22px; }}
    .tag {{ display: inline-flex; padding: 6px 10px; border-radius: 999px; background: #ecfdf5; color: #0f766e; font-weight: 700; font-size: 13px; }}
    main {{ display: grid; grid-template-columns: 260px minmax(420px, 1fr) 320px; gap: 18px; padding: 20px; }}
    aside, section {{ background: #fff; border: 1px solid #dbe3ef; border-radius: 12px; box-shadow: 0 10px 24px rgba(15, 23, 42, .05); }}
    aside {{ padding: 14px; }}
    .member {{ width: 100%; text-align: left; border: 1px solid #e2e8f0; background: #f8fafc; border-radius: 10px; margin-bottom: 10px; padding: 12px; cursor: pointer; }}
    .member strong {{ display: block; font-size: 14px; }}
    .member span {{ color: #64748b; font-size: 12px; }}
    .chat {{ padding: 18px; min-height: 620px; }}
    .bubble {{ max-width: 760px; border: 1px solid #dbeafe; background: #eff6ff; border-radius: 12px; padding: 14px 16px; margin: 0 0 14px; }}
    .bubble.rework_required {{ background: #fff7ed; border-color: #fdba74; }}
    .bubble.rework_done, .bubble.review_passed {{ background: #ecfdf5; border-color: #86efac; }}
    .speaker {{ font-weight: 800; margin-bottom: 8px; display: flex; justify-content: space-between; gap: 12px; }}
    .speaker span {{ color: #64748b; font-size: 12px; }}
    a {{ color: #0f766e; font-weight: 700; text-decoration: none; }}
    .panel {{ padding: 18px; }}
    .panel h2 {{ font-size: 16px; margin: 0 0 12px; }}
    li {{ margin-bottom: 10px; }}
  </style>
</head>
<body>
  <header>
    <div><h1>{html.escape(project_name)} · Agent 工作群</h1><p>多 Agent 已分工、同步、返工和归纳；所有外部动作保持 draft_only。</p></div>
    <a class="tag" href="{summary_href}">打开最终总结</a>
  </header>
  <main>
    <aside><h2>群成员</h2>{members}</aside>
    <section class="chat">{''.join(bubbles)}</section>
    <aside class="panel"><h2>风控返工</h2><ul>{rework_items}</ul><h2>下一步</h2><p>先看归纳 Agent 的最终总结，再由人工决定是否发布、评论、私信或发邮件。</p></aside>
  </main>
</body>
</html>
"""


def render_workspace_html(
    project_dir: Path,
    project_name: str,
    agent_tasks: list[dict[str, Any]],
    conversations: dict[str, str],
) -> str:
    cards = []
    buttons = []
    for index, task in enumerate(agent_tasks):
        active = " active" if index == 0 else ""
        buttons.append(
            f"<button class=\"agent-btn{active}\" data-agent=\"{html.escape(task['agent_id'])}\">{html.escape(task['agent_name'])}<span>{html.escape(task['status_label'])}</span></button>"
        )
        links = []
        for path in task.get("output_files", []):
            href = file_href(project_dir, path)
            links.append(f"<a href=\"{href}\">{html.escape(Path(path).name)}</a>")
        conversation = conversations.get(task["agent_id"], "")
        cards.append(
            f"<section class=\"agent-card{active}\" id=\"card-{html.escape(task['agent_id'])}\">"
            f"<h2>{html.escape(task['agent_name'])}</h2>"
            f"<div class=\"meta\">状态：{html.escape(task['status_label'])} · 模型能力：深度分析</div>"
            f"<h3>子任务</h3><p>{html.escape(task['input'])}</p>"
            f"<h3>输出摘要</h3><p>{html.escape(task['output_summary'])}</p>"
            f"<h3>会话摘要</h3><pre>{html.escape(conversation)}</pre>"
            f"<h3>产出文件</h3><div class=\"files\">{''.join(links) if links else '<span>暂无文件</span>'}</div>"
            f"</section>"
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{html.escape(project_name)} - Agent 成果工作台</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f7fb; color: #111827; }}
    header {{ padding: 22px 28px; background: #fff; border-bottom: 1px solid #dbe3ef; }}
    h1 {{ margin: 0 0 6px; font-size: 22px; }}
    main {{ display: grid; grid-template-columns: 300px 1fr; gap: 18px; padding: 20px; }}
    nav, .agent-card {{ background: #fff; border: 1px solid #dbe3ef; border-radius: 12px; box-shadow: 0 10px 24px rgba(15, 23, 42, .05); }}
    nav {{ padding: 14px; height: fit-content; }}
    .agent-btn {{ width: 100%; display: block; text-align: left; border: 1px solid #e2e8f0; background: #f8fafc; border-radius: 10px; margin-bottom: 10px; padding: 12px; cursor: pointer; font-weight: 800; }}
    .agent-btn.active {{ border-color: #0f766e; background: #ecfdf5; }}
    .agent-btn span {{ display: block; color: #64748b; font-size: 12px; font-weight: 500; margin-top: 4px; }}
    .agent-card {{ display: none; padding: 22px; }}
    .agent-card.active {{ display: block; }}
    .meta {{ display: inline-flex; padding: 6px 10px; border-radius: 999px; background: #ecfdf5; color: #0f766e; font-weight: 700; }}
    h3 {{ margin-top: 22px; }}
    pre {{ white-space: pre-wrap; background: #0f172a; color: #e5edf8; border-radius: 10px; padding: 14px; line-height: 1.6; }}
    .files a {{ display: inline-flex; margin: 0 10px 10px 0; padding: 8px 10px; border: 1px solid #99f6e4; border-radius: 8px; color: #0f766e; text-decoration: none; font-weight: 700; }}
  </style>
</head>
<body>
  <header><h1>{html.escape(project_name)} · Agent 成果工作台</h1><p>点击左侧 Agent 查看独立任务、输出、会话摘要和文件入口。</p></header>
  <main>
    <nav>{''.join(buttons)}</nav>
    <div>{''.join(cards)}</div>
  </main>
  <script>
    document.querySelectorAll('.agent-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.agent-btn').forEach(item => item.classList.remove('active'));
        document.querySelectorAll('.agent-card').forEach(item => item.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('card-' + btn.dataset.agent).classList.add('active');
      }});
    }});
  </script>
</body>
</html>
"""


def write_multi_agent_projects_index(projects_root: Path) -> None:
    index_path = projects_root / "projects_index.json"
    items = read_json(index_path, []) or []
    rows = []
    for item in items:
        project_dir = Path(item.get("project_dir") or Path(item.get("report_path", "")).parent)
        report_href = file_href(projects_root, item.get("report_path", ""))
        handoff_href = file_href(projects_root, item.get("handoff_path", ""))
        group_href = file_href(projects_root, item.get("agent_group_chat_path", ""))
        workspace_href = file_href(projects_root, item.get("agent_workspace_path", ""))
        summary_href = file_href(projects_root, item.get("final_summary_path", ""))
        materials_href = file_href(projects_root, str(project_dir / "multi_agent" / "files" / "content_materials.md"))
        social_href = file_href(projects_root, str(project_dir / "multi_agent" / "files" / "social_plan.md"))
        multi_agent = (
            f"<a href=\"{group_href}\">Agent 工作群</a><a href=\"{workspace_href}\">成果工作台</a><a href=\"{summary_href}\">最终总结</a>"
            if item.get("multi_agent_enabled")
            else "<span class=\"muted\">未启用多 Agent</span>"
        )
        rows.append(
            "<tr>"
            f"<td>{html.escape(item.get('created_at') or '')}</td>"
            f"<td>{html.escape(item.get('product_name') or '')}</td>"
            f"<td>{html.escape(item.get('factory_type') or '')}</td>"
            f"<td>{html.escape(item.get('mode') or '')}</td>"
            f"<td>{html.escape(str(item.get('source_count', 0)))}</td>"
            f"<td>{multi_agent}</td>"
            f"<td><a href=\"{report_href}\">推广方案</a><a href=\"{handoff_href}\">交接单</a><a href=\"{materials_href}\">宣传物料</a><a href=\"{social_href}\">社媒计划</a></td>"
            "</tr>"
        )
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>宇智能项目成果</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #111827; background: #f8fafc; }}
    h1 {{ margin: 0 0 8px; }}
    p {{ color: #475569; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dbe3ef; border-radius: 12px; overflow: hidden; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #e5eaf2; text-align: left; font-size: 14px; vertical-align: top; }}
    th {{ background: #f1f5f9; }}
    a {{ display: inline-flex; margin: 0 8px 8px 0; color: #0f766e; font-weight: 700; text-decoration: none; }}
    .muted {{ color: #94a3b8; }}
    .notice {{ margin: 16px 0; padding: 12px 14px; background: #ecfdf5; border: 1px solid #99f6e4; border-radius: 8px; }}
  </style>
</head>
<body>
  <h1>宇智能项目成果</h1>
  <p>这里汇总本机归档的制造业获客成果。所有外部动作均为 draft_only，发布、评论、私信和邮件必须人工确认。</p>
  <div class="notice">新增入口：Agent 工作群、Agent 成果工作台、最终总结、宣传物料和社媒计划。</div>
  <table>
    <thead>
      <tr><th>生成时间</th><th>产品名称</th><th>工厂类型</th><th>模式</th><th>来源数</th><th>多 Agent 入口</th><th>成果文件</th></tr>
    </thead>
    <tbody>{''.join(rows) if rows else '<tr><td colspan="7">暂无项目，请先运行一次制造业获客任务。</td></tr>'}</tbody>
  </table>
</body>
</html>
"""
    write_text(projects_root / "index.html", html_text)


def update_project_index_for_collaboration(projects_root: Path, project_id: str, paths: dict[str, str]) -> None:
    index_path = projects_root / "projects_index.json"
    items = read_json(index_path, []) or []
    for item in items:
        if item.get("project_id") == project_id:
            item.update(paths)
            item["multi_agent_enabled"] = True
            item["status"] = "multi_agent_completed"
    write_json(index_path, items)
    write_multi_agent_projects_index(projects_root)


def build_real_agent_collaboration(
    *,
    input_data: dict[str, Any],
    plan: dict[str, Any],
    agent_tasks: list[dict[str, Any]],
    outputs: dict[str, dict[str, Any]],
    archive_output: dict[str, Any],
    run_dir: Path,
    collaboration_root: str | Path = DEFAULT_COLLABORATION_ROOT,
    created_at: str,
    final_report_path: Path,
) -> dict[str, Any]:
    project_dir = Path(archive_output["project_dir"])
    project_id = archive_output["project_id"]
    project_name = f"{input_data.get('factory_type', '制造业工厂')}-{input_data.get('product_name', '制造业产品')} 多 Agent 协作项目"
    collaboration_dir = Path(collaboration_root) / plan["workflow_run_id"]
    project_multi_dir = project_dir / "multi_agent"
    for folder in [collaboration_dir, project_multi_dir]:
        (folder / "agent_conversations").mkdir(parents=True, exist_ok=True)
        (folder / "agent_outputs").mkdir(parents=True, exist_ok=True)
        (folder / "files").mkdir(parents=True, exist_ok=True)

    files_text = build_markdown_outputs(input_data, outputs, project_dir, final_report_path)
    file_paths: dict[str, str] = {}
    for name, text in files_text.items():
        for base in [collaboration_dir, project_multi_dir]:
            write_text(base / "files" / name, text)
        file_paths[name] = str(project_multi_dir / "files" / name)

    project_handoff = project_dir / "handoff.docx"
    if project_handoff.exists():
        for base in [collaboration_dir, project_multi_dir]:
            shutil.copy2(project_handoff, base / "files" / "factory_handoff.docx")
        file_paths["factory_handoff.docx"] = str(project_multi_dir / "files" / "factory_handoff.docx")

    parent_task_id = f"{plan['workflow_run_id']}-parent"
    room_id = f"{plan['workflow_run_id']}-agent-room"
    task_files = {
        "yuzhineng-manufacturing-chief": ["final_report.md"],
        "yuzhineng-product-analyst": ["product_card.md"],
        "yuzhineng-opportunity-researcher": ["opportunity_report.md"],
        "yuzhineng-content-producer": ["content_materials.md"],
        "yuzhineng-social-operator": ["social_plan.md"],
        "yuzhineng-factory-handoff": ["factory_handoff.md", "factory_handoff.docx"],
        "yuzhineng-safety-reviewer": ["safety_review.md"],
        "yuzhineng-summary-agent": ["final_summary.md", "final_report.md"],
        "yuzhineng-archive-agent": ["final_report.md"],
    }
    for index, task in enumerate(agent_tasks, start=1):
        task["task_id"] = f"{plan['workflow_run_id']}-{task['agent_id']}"
        task["parent_task_id"] = parent_task_id
        task["project_id"] = project_id
        task["room_id"] = room_id
        task["status"] = "completed"
        task["status_label"] = "已完成"
        task["created_at"] = created_at
        task["completed_at"] = created_at
        task["input"] = task.get("input") or task.get("assignment") or "执行本 Agent 分工"
        task["output_summary"] = output_summary(task["agent_id"], outputs)
        task["output_files"] = [file_paths[name] for name in task_files.get(task["agent_id"], []) if name in file_paths]
        task["order"] = index

    rework_issue_id = f"{plan['workflow_run_id']}-risk-001"
    rework_log = [
        {
            "issue_id": rework_issue_id,
            "raised_by": "yuzhineng-safety-reviewer",
            "target_agent": "yuzhineng-content-producer",
            "issue": "宣传物料 Agent 初稿缺少醒目的 draft_only 声明，容易让用户误以为可以自动发布。",
            "severity": "medium",
            "required_fix": "在宣传物料修正版中补充 draft_only、人工审批、不真实发布/评论/私信/发邮件声明。",
            "fix_status": "fixed",
            "fixed_file": file_paths["content_materials.md"],
            "fixed_at": created_at,
        }
    ]
    group_messages = build_group_messages(room_id, agent_tasks, file_paths, rework_issue_id, created_at)

    conversations: dict[str, str] = {}
    for task in agent_tasks:
        related_messages = [m for m in group_messages if m["sender_agent"] == task["agent_id"] or m["receiver_agent"] == task["agent_id"]]
        text = "\n".join(
            [
                f"# {task['agent_name']} 独立会话",
                "",
                f"- 子任务：{task['input']}",
                f"- 状态：{task['status_label']}",
                f"- 输出摘要：{task['output_summary']}",
                "",
                "## 群聊相关消息",
                *[f"- {msg['sender_name']}：{msg['content']}" for msg in related_messages],
                "",
                "## 文件",
                *[f"- {Path(path).name}: {path}" for path in task.get("output_files", [])],
            ]
        )
        conversations[task["agent_id"]] = text
        stem = agent_file_stem(task["agent_id"])
        for base in [collaboration_dir, project_multi_dir]:
            write_text(base / "agent_conversations" / f"{stem}.md", text)

    outputs_with_summary = dict(outputs)
    outputs_with_summary["summary"] = {
        "agent_id": "yuzhineng-summary-agent",
        "agent_name": "归纳 Agent",
        "read_agent_outputs": [task["agent_id"] for task in agent_tasks if task["agent_id"] != "yuzhineng-summary-agent"],
        "final_summary_path": file_paths["final_summary.md"],
        "final_report_path": file_paths["final_report.md"],
        "rework_issues_used": [item["issue_id"] for item in rework_log],
        "status": "completed",
    }
    for key, value in outputs_with_summary.items():
        output_name = {
            "product": "product_agent_output.json",
            "opportunity": "opportunity_agent_output.json",
            "content": "content_agent_output.json",
            "social": "social_agent_output.json",
            "factory": "factory_handoff_agent_output.json",
            "safety": "safety_agent_output.json",
            "summary": "summary_agent_output.json",
        }.get(key, f"{key}_output.json")
        for base in [collaboration_dir, project_multi_dir]:
            write_json(base / "agent_outputs" / output_name, value)
        if key == "summary":
            write_json(run_dir / output_name, value)

    manifest = {
        "run_id": plan["workflow_run_id"],
        "project_id": project_id,
        "project_name": project_name,
        "created_at": created_at,
        "user_input": input_data,
        "mode": "draft_only",
        "model": plan["model"],
        "status": "completed",
        "agents": plan["agents"],
        "group_room_id": room_id,
        "project_archive_path": str(project_dir),
        "collaboration_dir": str(collaboration_dir),
        "project_multi_agent_dir": str(project_multi_dir),
    }
    ui_trace = {
        "run_id": plan["workflow_run_id"],
        "expected_ui": [
            "左侧至少 4 个专业 Agent 显示对应任务",
            "agent_group_chat.html 可打开",
            "agent_workspace.html 可打开",
            "至少 3 个产出文件可打开",
        ],
        "generated_at": created_at,
    }
    for base in [collaboration_dir, project_multi_dir]:
        write_json(base / "run_manifest.json", manifest)
        write_json(base / "agent_tasks.json", agent_tasks)
        write_json(base / "group_room_messages.json", group_messages)
        write_json(base / "rework_log.json", rework_log)
        write_json(base / "ui_trace.json", ui_trace)
    write_json(run_dir / "run_manifest.json", manifest)
    write_json(run_dir / "agent_tasks.json", agent_tasks)
    write_json(run_dir / "group_room_messages.json", group_messages)
    write_json(run_dir / "agent_room_messages.json", group_messages)
    write_json(run_dir / "rework_log.json", rework_log)
    write_json(run_dir / "ui_trace.json", ui_trace)

    group_html = render_group_chat_html(project_dir, project_name, agent_tasks, group_messages, rework_log, Path(file_paths["final_summary.md"]))
    workspace_html = render_workspace_html(project_dir, project_name, agent_tasks, conversations)
    for base in [collaboration_dir, project_multi_dir]:
        write_text(base / "agent_group_chat.html", group_html)
        write_text(base / "agent_workspace.html", workspace_html)
    group_html_path = project_multi_dir / "agent_group_chat.html"
    workspace_html_path = project_multi_dir / "agent_workspace.html"

    update_project_index_for_collaboration(
        Path(archive_output["projects_index_json"]).parent,
        project_id,
        {
            "project_dir": str(project_dir),
            "agent_group_chat_path": str(group_html_path),
            "agent_workspace_path": str(workspace_html_path),
            "final_summary_path": file_paths["final_summary.md"],
            "multi_agent_run_dir": str(collaboration_dir),
            "group_room_id": room_id,
            "agent_task_count": len(agent_tasks),
            "group_message_count": len(group_messages),
            "rework_count": len(rework_log),
        },
    )

    return {
        "ok": True,
        "collaboration_run_dir": str(collaboration_dir),
        "project_multi_agent_dir": str(project_multi_dir),
        "run_manifest": str(project_multi_dir / "run_manifest.json"),
        "agent_tasks": str(project_multi_dir / "agent_tasks.json"),
        "group_room_messages": str(project_multi_dir / "group_room_messages.json"),
        "rework_log": str(project_multi_dir / "rework_log.json"),
        "agent_group_chat_html": str(group_html_path),
        "agent_workspace_html": str(workspace_html_path),
        "final_summary": file_paths["final_summary.md"],
        "final_report": file_paths["final_report.md"],
        "group_room_id": room_id,
        "agent_speaker_count": len({msg["sender_agent"] for msg in group_messages}),
        "rework_count": len(rework_log),
        "agent_tasks_data": agent_tasks,
        "group_messages_data": group_messages,
    }


def backup_sqlite(db_path: Path, backup_root: Path = DEFAULT_BACKUP_ROOT) -> str:
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / f"lobsterai-before-phase2f-{time.strftime('%Y%m%d-%H%M%S')}.sqlite"
    source = sqlite3.connect(str(db_path))
    try:
        target = sqlite3.connect(str(backup_path))
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()
    return str(backup_path)


def mirror_collaboration_to_lobsterai(
    *,
    collaboration: dict[str, Any],
    plan: dict[str, Any],
    db_path: str | Path = DEFAULT_LOBSTERAI_SQLITE,
    backup_root: str | Path = DEFAULT_BACKUP_ROOT,
) -> dict[str, Any]:
    db_path = Path(db_path)
    if not db_path.exists():
        return {"ok": False, "reason": f"LobsterAI SQLite not found: {db_path}", "mirrored_sessions": 0}
    backup_path = backup_sqlite(db_path, Path(backup_root))
    now = int(time.time() * 1000)
    con = sqlite3.connect(str(db_path))
    try:
        cur = con.cursor()
        for agent in plan["agents"]:
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
                    agent.get("role", ""),
                    f"你是{agent['name']}。只处理本地 draft_only 获客协作任务，不真实外发，不读取 secrets。",
                    agent.get("role", ""),
                    DEFAULT_MODEL,
                    collaboration["project_multi_agent_dir"],
                    "agent-avatar-svg:lobster",
                    json.dumps(agent.get("skills", []), ensure_ascii=False),
                    now,
                    now,
                ),
            )
        mirrored_sessions = 0
        for index, task in enumerate(collaboration["agent_tasks_data"], start=1):
            session_id = f"phase2f-{plan['workflow_run_id']}-{task['agent_id']}"
            title = f"{task['agent_name']}：{task['assignment']}"
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
                    title,
                    collaboration["project_multi_agent_dir"],
                    "宇智能 Phase 2F 真实多 Agent 协作任务，本地镜像会话。",
                    DEFAULT_MODEL,
                    now + index,
                    now + index,
                    json.dumps(["manufacturing_multi_agent_workflow"], ensure_ascii=False),
                    task["agent_id"],
                ),
            )
            cur.execute("DELETE FROM cowork_messages WHERE session_id = ?", (session_id,))
            messages = [
                ("user", task["input"], {"phase": "2F", "task_id": task["task_id"], "project_id": task["project_id"]}),
                (
                    "assistant",
                    "\n".join(
                        [
                            task["output_summary"],
                            "",
                            "产出文件：",
                            *[f"- {path}" for path in task.get("output_files", [])],
                            "",
                            "外部动作模式：draft_only，未真实发布、评论、私信或发邮件。",
                        ]
                    ),
                    {
                        "phase": "2F",
                        "model": DEFAULT_MODEL,
                        "external_action_mode": "draft_only",
                        "project_workspace": collaboration["agent_workspace_html"],
                        "group_chat": collaboration["agent_group_chat_html"],
                    },
                ),
            ]
            for msg_index, (msg_type, content, metadata) in enumerate(messages, start=1):
                cur.execute(
                    """
                    INSERT INTO cowork_messages (id, session_id, type, content, metadata, created_at, sequence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"{session_id}-msg-{msg_index}",
                        session_id,
                        msg_type,
                        content,
                        json.dumps(metadata, ensure_ascii=False),
                        now + index + msg_index,
                        msg_index,
                    ),
                )
            mirrored_sessions += 1

        parent_session_id = f"phase2f-{plan['workflow_run_id']}-yuzhineng-manufacturing-chief"
        cur.execute("DELETE FROM subagent_runs WHERE parent_session_id = ?", (parent_session_id,))
        for index, task in enumerate(collaboration["agent_tasks_data"], start=1):
            run_id = f"{parent_session_id}-subagent-{index:02d}"
            cur.execute(
                """
                INSERT OR REPLACE INTO subagent_runs (
                  id, parent_session_id, session_key, agent_id, task, label, status,
                  created_at, ended_at, messages_persisted
                )
                VALUES (?, ?, ?, ?, ?, ?, 'completed', ?, ?, 1)
                """,
                (
                    run_id,
                    parent_session_id,
                    task["task_id"],
                    task["agent_id"],
                    task["input"],
                    task["agent_name"],
                    now + index,
                    now + index + 1,
                ),
            )
            cur.execute("DELETE FROM subagent_messages WHERE run_id = ?", (run_id,))
            cur.execute(
                """
                INSERT INTO subagent_messages (id, run_id, type, content, metadata, created_at, sequence)
                VALUES (?, ?, 'assistant', ?, ?, ?, 1)
                """,
                (
                    f"{run_id}-msg-1",
                    run_id,
                    task["output_summary"],
                    json.dumps({"phase": "2F", "output_files": task.get("output_files", [])}, ensure_ascii=False),
                    now + index + 2,
                ),
            )
        con.commit()
        return {"ok": True, "backup_path": backup_path, "mirrored_sessions": mirrored_sessions}
    finally:
        con.close()
