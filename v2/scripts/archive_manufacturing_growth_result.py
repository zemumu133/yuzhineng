from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\OpenClaw")
V2 = ROOT / "v2"
DEFAULT_PROJECTS_ROOT = V2 / "projects"
DEFAULT_MODEL = "deepseek/deepseek-v4-pro"


class ArchiveError(RuntimeError):
    pass


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise ArchiveError(f"缺少必要文件：{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ArchiveError(f"JSON 读取失败：{path}，原因：{exc}") from exc


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
    return text or "manufacturing-growth"


def now_local_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def project_time_id(created_at: str | None) -> str:
    if created_at:
        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})", created_at)
        if match:
            year, month, day, hour, minute, second = match.groups()
            return f"{year}{month}{day}-{hour}{minute}{second}"
    return now_local_id()


def listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def item_title(item: Any) -> str:
    if isinstance(item, dict):
        return str(
            item.get("title")
            or item.get("theme")
            or item.get("intent")
            or item.get("scenario")
            or item.get("type")
            or item.get("day")
            or "项目"
        )
    return str(item)


def item_detail(item: Any) -> str:
    if isinstance(item, dict):
        for key in ("draft", "content_format", "priority", "pain_points", "decision_makers", "owner"):
            value = item.get(key)
            if value:
                return "、".join(str(v) for v in value) if isinstance(value, list) else str(value)
        return ""
    return ""


def md_list(items: Any) -> str:
    values = listify(items)
    if not values:
        return "- 暂无。"
    lines = []
    for item in values:
        title = item_title(item)
        detail = item_detail(item)
        lines.append(f"- {title}" + (f"：{detail}" if detail else ""))
    return "\n".join(lines)


def resolve_task_files(task_output_dir: Path) -> dict[str, Path]:
    return {
        "input": task_output_dir / "input.json",
        "skill_output": task_output_dir / "skill_output.json",
        "sources": task_output_dir / "sources.json",
        "search_trace": task_output_dir / "search_trace.json",
        "safety_check": task_output_dir / "safety_check.json",
        "summary": task_output_dir / "summary.md",
    }


def source_list(skill_output: dict[str, Any], files: dict[str, Path]) -> list[dict[str, Any]]:
    if files["sources"].exists():
        value = read_json(files["sources"], [])
        return value if isinstance(value, list) else []
    if files["search_trace"].exists():
        trace = read_json(files["search_trace"], {})
        value = trace.get("sources") if isinstance(trace, dict) else []
        return value if isinstance(value, list) else []
    value = skill_output.get("sources") or skill_output.get("public_sources") or []
    return value if isinstance(value, list) else []


def build_report_md(skill_output: dict[str, Any], sources: list[dict[str, Any]]) -> str:
    understanding = skill_output.get("product_understanding") or {}
    opportunity = skill_output.get("opportunity_discovery") or {}
    materials = skill_output.get("content_materials") or {}
    handoff = skill_output.get("factory_handoff_sheet") or {}
    product = understanding.get("product_name") or skill_output.get("product") or "制造业产品"
    factory_type = understanding.get("factory_type") or skill_output.get("industry") or "制造业工厂"
    source_status = skill_output.get("source_status") or opportunity.get("source_status") or "unknown"

    source_lines = []
    for source in sources:
        title = source.get("title") or "公开来源"
        url = source.get("url") or "unknown"
        snippet = source.get("snippet") or source.get("source_excerpt") or ""
        source_lines.append(f"- [{title}]({url})：{snippet}")
    if not source_lines:
        source_lines.append("- 暂无已验证公开来源；本轮结论仅作为待复核草稿。")

    return f"""# {product} 获客推广方案

## 1. 项目摘要

- 产品：{product}
- 工厂类型：{factory_type}
- 地区：{understanding.get('location') or skill_output.get('city') or 'unknown'}
- 模式：draft_only
- 来源状态：{source_status}

## 2. 产品理解

- 产品描述：{understanding.get('product_description') or '待补充'}
- 工厂能力：{'、'.join(understanding.get('factory_capabilities') or []) or '待补充'}
- 产品卖点：{'、'.join(understanding.get('selling_points') or []) or '待补充'}
- 适合客户：{'、'.join(understanding.get('suitable_customer_types') or []) or '待补充'}

## 3. 商机判断

- 商机评分：{opportunity.get('opportunity_score') or 'unknown'}
- 公开需求信号：{'、'.join(opportunity.get('public_demand_signals') or []) or '待补充'}

## 4. 目标客户类型

{md_list(skill_output.get('target_customer_segments') or skill_output.get('target_customer_types'))}

## 5. 公开来源摘要

{chr(10).join(source_lines)}

## 6. 小红书内容建议

{md_list(materials.get('xiaohongshu_notes'))}

## 7. 抖音内容建议

{md_list(materials.get('douyin_scripts'))}

## 8. 公众号内容建议

{md_list(materials.get('wechat_article_outline'))}

## 9. 评论回复草稿

{md_list(skill_output.get('comment_reply_drafts'))}

## 10. 私信草稿

{md_list(skill_output.get('dm_drafts'))}

## 11. 账号养成计划

{md_list(skill_output.get('account_nurturing_plan'))}

## 12. 工厂销售交接建议

- 交接标题：{handoff.get('handoff_title') or product + ' 客户交接单'}
- 推荐跟进人：{handoff.get('recommended_owner') or '工厂销售或老板'}
- 需求确认问题：
{md_list(handoff.get('qualification_questions'))}

## 13. 待办事项

{md_list(skill_output.get('todos'))}

## 14. 风险提醒

{md_list(skill_output.get('risk_notes'))}

## 15. 下一步建议

{md_list(skill_output.get('next_steps'))}

## 16. draft_only 声明

本项目所有内容均为 draft_only 草稿。尚未真实发布、评论、私信或发邮件；涉及报价、交期、认证、客户案例、联系方式和外部触达的动作必须人工复核后在外部平台手动执行。
"""


def docx_xml_escape(value: str) -> str:
    return html.escape(value, quote=False)


def paragraph(text: str) -> str:
    return f"<w:p><w:r><w:t xml:space=\"preserve\">{docx_xml_escape(text)}</w:t></w:r></w:p>"


def build_handoff_docx(path: Path, skill_output: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    understanding = skill_output.get("product_understanding") or {}
    handoff = skill_output.get("factory_handoff_sheet") or {}
    product = understanding.get("product_name") or skill_output.get("product") or "制造业产品"
    segments = skill_output.get("target_customer_segments") or skill_output.get("target_customer_types") or []
    first_segment = segments[0] if segments and isinstance(segments[0], dict) else {}
    source_title = sources[0].get("title") if sources else "unknown"
    lines = [
        "工厂销售客户交接单",
        f"客户线索来源：{source_title}",
        f"客户类型：{first_segment.get('type') or '待人工确认'}",
        f"需求判断：{'、'.join(first_segment.get('pain_points') or []) or '待人工确认'}",
        f"适合推荐的产品：{product}",
        "推荐跟进话术：先确认客户规格、数量、交期、使用场景和认证要求，再由工厂销售人工报价。",
        "报价/询盘信息待补充：规格、图纸/样品、数量、交期、包装、认证、收货地区。",
        f"工厂负责人：{handoff.get('recommended_owner') or '工厂销售或老板'}",
        "跟进状态：pending，等待人工复核。",
        "备注：所有内容为 draft_only 草稿，未真实发送、未私信、未评论、未发邮件。",
    ]
    body = "".join(paragraph(line) for line in lines)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
  </w:body>
</w:document>
"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document)


def build_readme(project_name: str, manifest: dict[str, Any]) -> str:
    return f"""# {project_name}

这个项目是宇智能为制造业获客任务生成的本地成果工作区。

## 已生成成果

- 推广方案：`report.md`
- 工厂销售交接单：`handoff.docx`
- 公开来源：`sources.json`
- 下一步待办：`todos.json`
- 安全检查：`safety_check.json`

## 下一步该做什么

1. 先人工复核产品规格、产能、认证、交期和价格边界。
2. 检查公开来源是否可信，删除不适合对外引用的内容。
3. 选择可公开的图片、车间、设备和产品素材。
4. 将评论、私信、发布和邮件内容作为草稿审批，不自动外发。

## 未执行动作

- 未真实发布。
- 未真实评论。
- 未真实私信。
- 未真实发邮件。
- 未登录社媒账号。

## 审批要求

所有外部动作均为 `{manifest['mode']}`，必须人工确认后在外部平台手动执行。
"""


def generated_file_paths(project_dir: Path) -> dict[str, str]:
    return {
        "report_md": str(project_dir / "report.md"),
        "handoff_docx": str(project_dir / "handoff.docx"),
        "readme": str(project_dir / "README_CN.md"),
        "todos": str(project_dir / "todos.json"),
        "sources": str(project_dir / "sources.json"),
        "safety_check": str(project_dir / "safety_check.json"),
    }


def build_manifest(
    project_id: str,
    project_name: str,
    project_dir: Path,
    input_data: dict[str, Any],
    skill_output: dict[str, Any],
    sources: list[dict[str, Any]],
    todos: list[Any],
    safety: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    understanding = skill_output.get("product_understanding") or {}
    target_customers = (
        input_data.get("target_customer_hint")
        or input_data.get("target_customers")
        or input_data.get("targets")
        or skill_output.get("target_customer_segments")
        or []
    )
    return {
        "project_id": project_id,
        "project_name": project_name,
        "created_at": created_at,
        "product_name": understanding.get("product_name") or input_data.get("product_name") or skill_output.get("product"),
        "factory_type": understanding.get("factory_type") or input_data.get("factory_type") or skill_output.get("industry"),
        "company_location": understanding.get("location") or input_data.get("company_location") or skill_output.get("city"),
        "target_customers": target_customers,
        "platforms": input_data.get("platforms") or ["小红书", "抖音", "公众号"],
        "model": DEFAULT_MODEL,
        "mode": "draft_only",
        "source_status": skill_output.get("source_status") or "unknown",
        "generated_files": generated_file_paths(project_dir),
        "todos": todos,
        "safety_status": {
            "external_action_mode": safety.get("external_action_mode") or "draft_only",
            "real_external_send": bool(safety.get("real_external_send", False)),
            "real_email_sent": bool(safety.get("real_email_sent", False)),
            "real_dm_sent": bool(safety.get("real_dm_sent", False)),
            "real_comment_posted": bool(safety.get("real_comment_posted", False)),
            "real_post_published": bool(safety.get("real_post_published", False)),
            "read_secrets": bool(safety.get("read_secrets", False)),
        },
        "source_count": len(sources),
        "project_dir": str(project_dir),
    }


def update_projects_index(projects_root: Path, manifest: dict[str, Any]) -> None:
    index_path = projects_root / "projects_index.json"
    existing = read_json(index_path, []) if index_path.exists() else []
    existing = [item for item in existing if item.get("project_id") != manifest["project_id"]]
    existing.append(
        {
            "project_id": manifest["project_id"],
            "project_name": manifest["project_name"],
            "created_at": manifest["created_at"],
            "factory_type": manifest["factory_type"],
            "product_name": manifest["product_name"],
            "status": "draft_generated",
            "mode": "draft_only",
            "report_path": manifest["generated_files"]["report_md"],
            "handoff_path": manifest["generated_files"]["handoff_docx"],
            "todo_count": len(manifest.get("todos") or []),
            "source_count": manifest.get("source_count", 0),
        }
    )
    existing.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    write_json(index_path, existing)
    write_projects_html(projects_root, existing)


def file_href(index_dir: Path, target: str) -> str:
    try:
        relative = Path(target).resolve().relative_to(index_dir.resolve())
        return html.escape(relative.as_posix())
    except Exception:
        return "file:///" + html.escape(Path(target).as_posix())


def write_projects_html(projects_root: Path, index: list[dict[str, Any]]) -> None:
    rows = []
    for item in index:
        report_href = file_href(projects_root, item.get("report_path", ""))
        handoff_href = file_href(projects_root, item.get("handoff_path", ""))
        project_dir = Path(item.get("report_path", "")).parent
        todos_href = file_href(projects_root, str(project_dir / "todos.json"))
        rows.append(
            "<tr>"
            f"<td>{html.escape(item.get('created_at') or '')}</td>"
            f"<td>{html.escape(item.get('product_name') or '')}</td>"
            f"<td>{html.escape(item.get('factory_type') or '')}</td>"
            f"<td>{html.escape(item.get('mode') or '')}</td>"
            f"<td>{item.get('source_count', 0)}</td>"
            f"<td>{item.get('todo_count', 0)}</td>"
            f"<td><a href=\"{report_href}\">打开推广方案</a></td>"
            f"<td><a href=\"{handoff_href}\">打开交接单</a></td>"
            f"<td><a href=\"{todos_href}\">打开待办</a></td>"
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
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dbe3ef; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #e5eaf2; text-align: left; font-size: 14px; }}
    th {{ background: #f1f5f9; }}
    a {{ color: #0f766e; font-weight: 600; text-decoration: none; }}
    .notice {{ margin: 16px 0; padding: 12px 14px; background: #ecfdf5; border: 1px solid #99f6e4; border-radius: 8px; }}
  </style>
</head>
<body>
  <h1>宇智能项目成果</h1>
  <p>这里汇总本机归档的制造业获客成果。所有外部动作均为 draft_only，发布、评论、私信和邮件必须人工确认。</p>
  <div class="notice">项目索引文件：projects_index.json</div>
  <table>
    <thead>
      <tr><th>生成时间</th><th>产品</th><th>工厂类型</th><th>模式</th><th>来源</th><th>待办</th><th>推广方案</th><th>交接单</th><th>待办</th></tr>
    </thead>
    <tbody>
      {''.join(rows) if rows else '<tr><td colspan="9">暂无项目，请先运行一次制造业获客任务。</td></tr>'}
    </tbody>
  </table>
</body>
</html>
"""
    write_text(projects_root / "index.html", html_text)


def copy_or_generate_report(project_dir: Path, skill_output: dict[str, Any], sources: list[dict[str, Any]], source_file: Path | None) -> None:
    target = project_dir / "report.md"
    if source_file and source_file.exists():
        shutil.copy2(source_file, target)
    else:
        write_text(target, build_report_md(skill_output, sources))


def copy_or_generate_docx(project_dir: Path, skill_output: dict[str, Any], sources: list[dict[str, Any]], source_file: Path | None) -> None:
    target = project_dir / "handoff.docx"
    if source_file and source_file.exists():
        shutil.copy2(source_file, target)
    else:
        build_handoff_docx(target, skill_output, sources)


def archive_task_output(
    task_output_dir: str | Path,
    *,
    projects_root: str | Path = DEFAULT_PROJECTS_ROOT,
    project_slug: str | None = None,
    project_name: str | None = None,
    created_at: str | None = None,
    report_source: str | Path | None = None,
    handoff_source: str | Path | None = None,
) -> dict[str, Any]:
    task_output_dir = Path(task_output_dir)
    projects_root = Path(projects_root)
    files = resolve_task_files(task_output_dir)
    input_data = read_json(files["input"], {})
    skill_output = read_json(files["skill_output"])
    sources = source_list(skill_output, files)
    safety = read_json(files["safety_check"], {})
    todos = skill_output.get("todos") or []
    created_at = created_at or time.strftime("%Y-%m-%dT%H:%M:%S%z")
    created_id = project_time_id(created_at)

    understanding = skill_output.get("product_understanding") or {}
    product_name = understanding.get("product_name") or input_data.get("product_name") or skill_output.get("product") or "制造业获客"
    factory_type = understanding.get("factory_type") or input_data.get("factory_type") or skill_output.get("industry") or "制造业工厂"
    project_name = project_name or f"{factory_type}-{product_name}"
    slug = safe_slug(project_slug or f"{factory_type}-{product_name}")
    project_id = f"{created_id}-{slug}"
    project_dir = projects_root / project_id
    if project_dir.exists():
        project_dir = projects_root / f"{project_id}-{now_local_id()}"
        project_id = project_dir.name
    project_dir.mkdir(parents=True, exist_ok=False)

    write_json(project_dir / "input.json", input_data)
    write_json(project_dir / "sources.json", sources)
    write_json(project_dir / "skill_output.json", skill_output)
    write_json(project_dir / "todos.json", todos)
    if not safety:
        safety = {"external_action_mode": "draft_only", "real_external_send": False}
    write_json(project_dir / "safety_check.json", safety)

    copy_or_generate_report(project_dir, skill_output, sources, Path(report_source) if report_source else None)
    copy_or_generate_docx(project_dir, skill_output, sources, Path(handoff_source) if handoff_source else None)

    manifest = build_manifest(project_id, project_name, project_dir, input_data, skill_output, sources, todos, safety, created_at)
    write_json(project_dir / "project_manifest.json", manifest)
    write_text(project_dir / "README_CN.md", build_readme(project_name, manifest))
    update_projects_index(projects_root, manifest)

    return {
        "ok": True,
        "project_id": project_id,
        "project_dir": str(project_dir),
        "manifest_path": str(project_dir / "project_manifest.json"),
        "report_path": str(project_dir / "report.md"),
        "handoff_path": str(project_dir / "handoff.docx"),
        "projects_index_json": str(projects_root / "projects_index.json"),
        "projects_index_html": str(projects_root / "index.html"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="归档制造业获客成果到宇智能项目工作区")
    parser.add_argument("--task-output-dir", required=True, help="Phase 2B/2C 任务输出目录，需包含 input.json 和 skill_output.json")
    parser.add_argument("--projects-root", default=str(DEFAULT_PROJECTS_ROOT), help="项目工作区根目录")
    parser.add_argument("--project-slug", default="", help="项目目录短名，留空则自动生成")
    parser.add_argument("--project-name", default="", help="用户可读项目名")
    parser.add_argument("--created-at", default="", help="ISO 时间，留空使用当前时间")
    parser.add_argument("--report-source", default="", help="可选：已有 Markdown 推广方案")
    parser.add_argument("--handoff-source", default="", help="可选：已有 docx 交接单")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = archive_task_output(
            args.task_output_dir,
            projects_root=args.projects_root,
            project_slug=args.project_slug or None,
            project_name=args.project_name or None,
            created_at=args.created_at or None,
            report_source=args.report_source or None,
            handoff_source=args.handoff_source or None,
        )
    except ArchiveError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
