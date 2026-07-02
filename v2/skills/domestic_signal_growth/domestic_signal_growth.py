from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from search_adapter import SearchAdapter, now_iso


DEFAULT_INPUT = {
    "product": "职业证书考评服务",
    "industry": "教育培训",
    "target_customers": ["培训机构", "人力资源公司"],
    "city": "全国",
    "platforms": ["小红书", "抖音"],
    "mode": "draft_only",
    "search_required": True,
}


def generate_signal_report(payload: dict[str, Any], searcher: Any | None = None) -> dict[str, Any]:
    task = normalize_input(payload)
    query = build_search_query(task)
    searcher = searcher or SearchAdapter()
    if task["search_required"]:
        search_result = searcher.search(
            query,
            max_results=5,
            manual_seed_urls=task.get("manual_seed_urls"),
            provider_mode=task.get("search_provider", "existing_lobster_web_search"),
        )
    else:
        search_result = {
            "provider": "no_source_available",
            "query": query,
            "source_status": "unverified",
            "sources": [],
            "errors": ["本次输入设置 search_required=false，未执行公开搜索。"],
            "attempts": [{"provider": "no_source_available", "ok": False}],
            "fetched_at": now_iso(),
        }

    template = choose_template(task)
    sources = search_result.get("sources") or []
    source_status = search_result.get("source_status") or ("verified_public_sources" if sources else "unverified")
    risk_notes = list(template["risk_notes"])
    if not sources:
        risk_notes.append("没有真实公开来源时，本轮结论只能作为待验证假设，不能对外引用为事实。")
    if task["mode"] != "draft_only":
        risk_notes.append("输入模式已被强制改为 draft_only，外部动作必须人工审批后在外部平台处理。")
    risk_notes.append("不得真实发布、评论、私信或发邮件；本 Skill 只生成草稿和人工待办。")

    output = {
        "skill": "domestic_signal_growth",
        "product": task["product"],
        "industry": task["industry"],
        "city": task["city"],
        "mode": "draft_only",
        "source_status": source_status,
        "sources": sources,
        "search_trace": {
            "query": query,
            "provider": search_result.get("provider"),
            "attempts": search_result.get("attempts", []),
            "errors": search_result.get("errors", []),
            "fetched_at": search_result.get("fetched_at"),
        },
        "opportunity_judgement": build_opportunity(task, template, source_status, len(sources)),
        "target_customer_types": template["target_customer_types"],
        "platform_strategy": build_platform_strategy(task, template),
        "followup_drafts": build_followup_drafts(task, template),
        "todos": build_todos(task, template),
        "risk_notes": risk_notes,
        "next_steps": build_next_steps(task, sources),
        "generated_at": now_iso(),
    }
    return output


def normalize_input(payload: dict[str, Any]) -> dict[str, Any]:
    merged = dict(DEFAULT_INPUT)
    merged.update(payload or {})
    merged["product"] = str(merged.get("product") or DEFAULT_INPUT["product"]).strip()
    merged["industry"] = str(merged.get("industry") or DEFAULT_INPUT["industry"]).strip()
    merged["city"] = str(merged.get("city") or "全国").strip()
    merged["target_customers"] = normalize_list(merged.get("target_customers") or merged.get("targets") or DEFAULT_INPUT["target_customers"])
    merged["platforms"] = normalize_list(merged.get("platforms") or DEFAULT_INPUT["platforms"])
    merged["mode"] = "draft_only"
    merged["search_required"] = bool(merged.get("search_required", True))
    return merged


def normalize_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def build_search_query(task: dict[str, Any]) -> str:
    targets = " ".join(task["target_customers"])
    platforms = " ".join(task["platforms"])
    return f"{task['product']} {task['industry']} {targets} 获客 内容营销 {platforms} 公开信息"


def choose_template(task: dict[str, Any]) -> dict[str, Any]:
    text = f"{task['product']} {task['industry']} {' '.join(task['target_customers'])}"
    if any(keyword in text for keyword in ["包装", "纸箱", "仓储", "物流", "工厂"]):
        return heavy_packaging_template()
    if any(keyword in text for keyword in ["健身", "器材", "经销商", "跨境"]):
        return fitness_equipment_template()
    if any(keyword in text for keyword in ["证书", "考评", "培训", "人力资源", "教育"]):
        return certificate_training_template()
    return generic_template(task)


def build_opportunity(task: dict[str, Any], template: dict[str, Any], source_status: str, source_count: int) -> dict[str, Any]:
    if source_status == "verified_public_sources":
        confidence = 0.78
        source_note = f"已获得 {source_count} 条公开来源，可作为第一轮信号参考。"
    elif source_status == "search_failed":
        confidence = 0.45
        source_note = "公开搜索失败，当前判断需要人工补充来源后复核。"
    else:
        confidence = 0.52
        source_note = "暂未获得公开来源，当前判断只能作为内部假设。"
    return {
        "level": template["opportunity_level"],
        "reason": f"{task['product']} 面向 {'、'.join(task['target_customers'])} 有明确的内容获客切入点：{template['opportunity_reason']} {source_note}",
        "confidence": confidence,
    }


def build_platform_strategy(task: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    strategy: dict[str, Any] = {}
    platforms = set(task["platforms"])
    if "小红书" in platforms:
        strategy["xiaohongshu"] = template["platform_strategy"]["xiaohongshu"]
    if "抖音" in platforms:
        strategy["douyin"] = template["platform_strategy"]["douyin"]
    if "公众号" in platforms or "微信" in platforms:
        strategy["wechat_official_account"] = template["platform_strategy"].get("wechat_official_account", {
            "positioning": "承接深度说明和人工咨询入口",
            "content_ideas": ["整理一篇常见问题和适用客户说明"],
            "notes": ["文章中不要放绝对承诺，联系方式由人工确认后发布。"],
        })
    return strategy


def build_followup_drafts(task: dict[str, Any], template: dict[str, Any]) -> list[dict[str, Any]]:
    target_text = "、".join(task["target_customers"])
    drafts = []
    for item in template["followup_drafts"]:
        drafts.append(
            {
                "scenario": item["scenario"],
                "draft": item["draft"].format(product=task["product"], targets=target_text),
                "risk_level": item["risk_level"],
            }
        )
    return drafts


def build_todos(task: dict[str, Any], template: dict[str, Any]) -> list[dict[str, Any]]:
    todos = []
    for item in template["todos"]:
        todos.append(
            {
                "title": item["title"].format(product=task["product"]),
                "owner": item["owner"],
                "priority": item["priority"],
                "requires_approval": True,
            }
        )
    return todos


def build_next_steps(task: dict[str, Any], sources: list[dict[str, Any]]) -> list[str]:
    steps = [
        f"人工查看 {task['product']} 的公开来源，筛掉不相关或疑似广告页。",
        "从输出的话术中挑 1-2 条改成自己的表达，先小范围人工验证。",
        "所有发布、评论、私信、邮件都保持人工审批，不自动发送。",
    ]
    if not sources:
        steps.insert(0, "先补充 3-5 个公开网页 URL 或重新运行公开搜索，再决定是否触达。")
    return steps


def certificate_training_template() -> dict[str, Any]:
    return {
        "opportunity_level": "medium",
        "opportunity_reason": "培训机构和人力资源公司需要把证书项目讲清楚，同时必须控制合规宣传边界。",
        "target_customer_types": [
            {
                "type": "职业培训机构",
                "pain_points": ["招生线索不稳定", "证书项目解释成本高", "合规宣传边界难把握"],
                "buying_signals": ["持续发布招生笔记", "官网有证书培训栏目", "近期增加企业培训项目"],
                "decision_makers": ["校区负责人", "招生负责人", "课程产品负责人"],
            },
            {
                "type": "人力资源服务公司",
                "pain_points": ["企业客户需要培训方案", "岗位能力证明内容难包装", "销售跟进资料分散"],
                "buying_signals": ["发布企业培训服务", "服务对象包含用工企业", "有职业能力提升相关业务"],
                "decision_makers": ["业务负责人", "企业培训负责人", "市场负责人"],
            },
        ],
        "platform_strategy": {
            "xiaohongshu": {
                "positioning": "用通俗科普和避坑笔记建立信任",
                "content_ideas": ["职业证书考评适合哪些人", "培训机构做证书项目最容易踩的 3 个坑", "HR 怎么向企业解释证书培训价值"],
                "notes": ["避免包过、保就业、保收入等承诺。"],
            },
            "douyin": {
                "positioning": "用短视频讲清政策口径、适用人群和报名注意事项",
                "content_ideas": ["60 秒讲清证书考评和培训服务的区别", "培训机构招生话术如何避免过度承诺", "企业 HR 为什么会关注职业能力证明"],
                "notes": ["不要虚构官方背书或合作案例。"],
            },
        },
        "followup_drafts": [
            {
                "scenario": "公开评论草稿",
                "draft": "看到您在做{product}相关内容，这类项目最难的是既讲清价值又不越过合规边界。我们可以先做一版不外发的小红书/抖音选题和人工跟进草稿，供您内部参考。",
                "risk_level": "medium",
            },
            {
                "scenario": "私信草稿",
                "draft": "您好，我们在做 AI 获客和内容运营工作流，适合帮{targets}梳理{product}的公开内容选题、风险提示和人工待办。本轮只生成草稿，不自动私信或发布。",
                "risk_level": "medium",
            },
        ],
        "todos": [
            {"title": "补充{product}涉及的证书类别和宣传禁用词", "owner": "human", "priority": "high"},
            {"title": "生成 5 条合规科普笔记草稿", "owner": "ai_draft", "priority": "medium"},
            {"title": "人工确认是否允许对外使用来源链接", "owner": "human", "priority": "high"},
        ],
        "risk_notes": ["证书类内容必须避免暗示官方背书、包过、保就业或收入承诺。"],
    }


def heavy_packaging_template() -> dict[str, Any]:
    return {
        "opportunity_level": "medium",
        "opportunity_reason": "重货和仓储场景关注破损、承重、定制和交付稳定性，适合用工艺说明和案例型内容获客。",
        "target_customer_types": [
            {
                "type": "电商仓储团队",
                "pain_points": ["重货发货破损率高", "纸箱规格多但复购管理混乱", "促销期交付压力大"],
                "buying_signals": ["仓库扩容", "重货类目增加", "公开招聘仓储/包装岗位"],
                "decision_makers": ["仓储负责人", "采购负责人", "运营负责人"],
            },
            {
                "type": "制造工厂",
                "pain_points": ["出厂包装承重不足", "异形件定制周期长", "运输损耗影响客户验收"],
                "buying_signals": ["官网展示设备/零部件产品", "有外发物流需求", "发布供应链升级信息"],
                "decision_makers": ["采购经理", "生产负责人", "供应链负责人"],
            },
            {
                "type": "物流公司",
                "pain_points": ["客户货损纠纷", "包装方案标准化不足", "旺季耗材采购波动"],
                "buying_signals": ["承接大件/重货物流", "发布包装增值服务", "扩展仓配一体业务"],
                "decision_makers": ["网点负责人", "大客户经理", "运营经理"],
            },
        ],
        "platform_strategy": {
            "xiaohongshu": {
                "positioning": "用实拍对比和避坑内容解释重型纸箱价值",
                "content_ideas": ["重货发货为什么普通纸箱容易破", "仓库选重型纸箱看这 4 个指标", "电商仓储如何降低包装返工"],
                "notes": ["不虚构客户货损数据，真实数据需人工确认。"],
            },
            "douyin": {
                "positioning": "用短视频展示承重、抗压、定制流程和包装前后对比",
                "content_ideas": ["重型纸箱承重测试怎么拍才可信", "工厂大件发货包装流程拆解", "物流货损常见包装问题演示"],
                "notes": ["测试画面必须基于真实材料，不夸大承重参数。"],
            },
            "wechat_official_account": {
                "positioning": "承接 B2B 采购决策，输出工艺说明、选型表和询价清单",
                "content_ideas": ["重型包装纸箱采购避坑清单", "电商仓储包装规格管理表", "工厂出货包装验收要点"],
                "notes": ["涉及价格和交期必须人工确认。"],
            },
        },
        "followup_drafts": [
            {
                "scenario": "公开评论草稿",
                "draft": "重货包装最怕看起来省钱、最后货损和返工更贵。我们可以先帮您把{product}整理成选型清单、短视频脚本和人工询盘话术，不自动外发。",
                "risk_level": "low",
            },
            {
                "scenario": "私信草稿",
                "draft": "您好，看到您面向{targets}做业务。我们在做 AI 获客和内容运营系统，可以先基于公开信息生成{product}的内容选题、采购痛点和跟进草稿，您确认后再人工使用。",
                "risk_level": "medium",
            },
        ],
        "todos": [
            {"title": "补充{product}的承重范围、材质、规格和交期边界", "owner": "human", "priority": "high"},
            {"title": "生成 5 条工艺/选型类内容草稿", "owner": "ai_draft", "priority": "medium"},
            {"title": "人工确认可公开展示的测试图和案例", "owner": "human", "priority": "high"},
        ],
        "risk_notes": ["包装承重、货损率、交期和价格必须基于真实数据，不能虚构客户案例。"],
    }


def fitness_equipment_template() -> dict[str, Any]:
    return {
        "opportunity_level": "medium",
        "opportunity_reason": "健身房、经销商和跨境卖家都需要产品差异化、场景展示和售前资料，适合用内容种草加人工询盘承接。",
        "target_customer_types": [
            {
                "type": "健身房和私教工作室",
                "pain_points": ["新店设备选型困难", "空间利用率和会员体验难平衡", "售后维护担心影响营业"],
                "buying_signals": ["发布新店筹备", "装修升级", "课程扩展或团课增长"],
                "decision_makers": ["店长", "投资人", "运营负责人"],
            },
            {
                "type": "健身器材经销商",
                "pain_points": ["产品卖点同质化", "招商素材不足", "终端客户问答资料不统一"],
                "buying_signals": ["招募代理", "发布展会信息", "扩展产品线"],
                "decision_makers": ["老板", "渠道负责人", "销售负责人"],
            },
            {
                "type": "跨境卖家",
                "pain_points": ["选品差异化不足", "内容素材本地化困难", "售后和参数说明需要标准化"],
                "buying_signals": ["运营健身类 SKU", "关注海外平台内容", "招募供应链或选品岗位"],
                "decision_makers": ["选品负责人", "跨境运营负责人", "老板"],
            },
        ],
        "platform_strategy": {
            "xiaohongshu": {
                "positioning": "用场景化种草和选购指南吸引健身房、工作室和经销商",
                "content_ideas": ["小型健身房第一批器材怎么配", "经销商介绍器材别只讲参数", "家用和商用健身器材差别在哪"],
                "notes": ["不承诺减脂效果或医疗效果。"],
            },
            "douyin": {
                "positioning": "用演示视频、空间布局和对比讲解提升询盘",
                "content_ideas": ["30 秒看懂一套力量区怎么规划", "健身器材经销商怎么拍产品卖点", "跨境健身器材短视频素材怎么做"],
                "notes": ["器械安全、承重、质保信息必须人工确认。"],
            },
            "wechat_official_account": {
                "positioning": "承接 B2B 询盘，沉淀选型表、报价准备清单和常见问题",
                "content_ideas": ["健身房开店器材清单模板", "经销商合作前需要确认的 8 件事", "跨境健身器材素材和参数规范"],
                "notes": ["报价、质保、认证信息不得自动生成最终承诺。"],
            },
        },
        "followup_drafts": [
            {
                "scenario": "公开评论草稿",
                "draft": "健身器材推广很适合先把场景、空间和售后问题讲清楚。我们可以先帮您把{product}整理成小红书/抖音内容草稿和人工跟进待办，不自动发布。",
                "risk_level": "low",
            },
            {
                "scenario": "私信草稿",
                "draft": "您好，看到您可能面向{targets}做健身器材相关业务。我们在做 AI 获客系统，可以基于公开信息整理客户类型、内容方向和询盘草稿，全程 draft_only。",
                "risk_level": "medium",
            },
        ],
        "todos": [
            {"title": "补充{product}的型号、价格区间、质保和认证边界", "owner": "human", "priority": "high"},
            {"title": "生成 5 条器材场景演示脚本", "owner": "ai_draft", "priority": "medium"},
            {"title": "人工确认是否区分内贸与跨境素材", "owner": "human", "priority": "medium"},
        ],
        "risk_notes": ["不得承诺健身效果、医疗改善或未确认的认证资质。"],
    }


def generic_template(task: dict[str, Any]) -> dict[str, Any]:
    targets = task["target_customers"] or ["目标客户"]
    return {
        "opportunity_level": "medium",
        "opportunity_reason": "目标客户有公开内容获客和人工跟进需求，适合先做公开信息研究。",
        "target_customer_types": [
            {
                "type": target,
                "pain_points": ["内容生产不稳定", "线索判断缺少标准", "人工跟进资料分散"],
                "buying_signals": ["持续发布业务内容", "近期扩展服务", "公开招聘市场/销售岗位"],
                "decision_makers": ["老板", "市场负责人", "销售负责人"],
            }
            for target in targets
        ],
        "platform_strategy": {
            "xiaohongshu": {
                "positioning": "用问题拆解和经验型内容建立信任",
                "content_ideas": [f"{task['product']}适合哪些客户", f"{targets[0]}选择服务前要问的 5 个问题"],
                "notes": ["不要虚构案例或收益数据。"],
            },
            "douyin": {
                "positioning": "用短视频解释服务流程、避坑和常见误区",
                "content_ideas": [f"60 秒讲清{task['product']}的适用场景", "客户常见误区拆解"],
                "notes": ["所有承诺使用保守表达。"],
            },
        },
        "followup_drafts": [
            {
                "scenario": "私信草稿",
                "draft": "您好，我们在做 AI 获客和内容运营系统，可以先帮{targets}梳理{product}的公开内容方向和人工待办，全程只生成草稿。",
                "risk_level": "medium",
            }
        ],
        "todos": [
            {"title": "补充{product}的具体服务边界", "owner": "human", "priority": "high"},
            {"title": "生成首轮内容选题和人工跟进草稿", "owner": "ai_draft", "priority": "medium"},
        ],
        "risk_notes": ["不得虚构案例、收入数据、合作经历或联系方式。"],
    }


def read_input(args: argparse.Namespace) -> dict[str, Any]:
    if args.input_file:
        return json.loads(Path(args.input_file).read_text(encoding="utf-8"))
    if args.input_json:
        return json.loads(args.input_json)
    raw = sys.stdin.read().strip()
    if raw:
        return json.loads(raw)
    return dict(DEFAULT_INPUT)


def main() -> int:
    parser = argparse.ArgumentParser(description="domestic_signal_growth MVP")
    parser.add_argument("--input-json", default="")
    parser.add_argument("--input-file", default="")
    parser.add_argument("--output-file", default="")
    args = parser.parse_args()

    payload = read_input(args)
    output = generate_signal_report(payload)
    text = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output_file:
        Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_file).write_text(text + "\n", encoding="utf-8", newline="\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
