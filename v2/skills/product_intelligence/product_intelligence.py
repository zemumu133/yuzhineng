from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_PLATFORMS = ["小红书", "抖音", "公众号"]


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def text_of(payload: dict[str, Any]) -> str:
    values = [
        payload.get("factory_type"),
        payload.get("product_name"),
        payload.get("product_description"),
        " ".join(normalize_list(payload.get("materials"))),
        " ".join(normalize_list(payload.get("factory_capabilities"))),
        " ".join(normalize_list(payload.get("typical_customers"))),
    ]
    return " ".join(str(value or "") for value in values)


def infer_category(payload: dict[str, Any]) -> str:
    text = text_of(payload)
    if any(keyword in text for keyword in ["包装", "纸箱", "瓦楞", "物流包装", "出口包装"]):
        return "heavy_packaging"
    if any(keyword in text for keyword in ["健身", "哑铃", "力量训练", "包胶", "器材"]):
        return "fitness_equipment"
    if any(keyword in text for keyword in ["电子", "连接件", "线束", "充电", "铜件", "线材"]):
        return "electronics_parts"
    return "generic_manufacturing"


def missing_information(payload: dict[str, Any]) -> list[str]:
    checks = [
        ("product_description", "产品描述"),
        ("materials", "材料"),
        ("factory_capabilities", "工厂能力"),
        ("certifications", "认证"),
        ("delivery_cycle", "交期"),
        ("price_range", "价格区间"),
        ("typical_customers", "典型客户"),
    ]
    missing = []
    for key, label in checks:
        value = payload.get(key)
        if isinstance(value, list):
            is_empty = len(normalize_list(value)) == 0
        else:
            is_empty = not str(value or "").strip()
        if is_empty:
            missing.append(f"缺少{label}，需要人工补充后再用于报价、交期或客户承诺。")
    return missing


def category_rules(category: str) -> dict[str, Any]:
    rules = {
        "heavy_packaging": {
            "category": "重型包装与物流包装",
            "selling_points": [
                ("抗压承重", "适合重货、电商仓储和长途运输，重点证明抗压和破损控制。"),
                ("尺寸定制", "客户常需要按产品尺寸、装箱方式和出口标准定制。"),
                ("出口包装经验", "外贸客户关注运输损耗、唛头、印刷和包装规范。"),
            ],
            "segments": [
                ("电商仓储", "关注爆单后的发货稳定、货损控制和包装成本。", ["老板", "仓储负责人", "运营"], ["破损率高", "大促备货", "包装规格不统一"]),
                ("制造工厂", "需要按产品重量和出货方式定制包装。", ["采购", "生产主管", "老板"], ["新品出货", "换包装供应商", "降低运输损耗"]),
                ("物流公司", "关注不同货型的承重和装卸便利性。", ["运营", "采购"], ["客户货损投诉", "承接新线路", "包装升级"]),
                ("外贸企业", "关注出口包装、唛头印刷和装柜稳定性。", ["外贸业务", "采购", "老板"], ["出货旺季", "客户验货", "海外退损"]),
            ],
            "scenarios": ["重货发货", "电商仓储备货", "外贸出口装柜", "制造工厂成品出货"],
            "xiaohongshu": ["重货纸箱怎么选才不容易破", "电商仓储发货前要确认的包装参数", "出口纸箱定制避坑清单"],
            "douyin": ["30 秒看懂重型纸箱抗压测试", "仓库发货纸箱为什么总破损", "外贸出口包装打样流程"],
            "wechat": ["重型包装纸箱采购清单", "外贸出口包装常见问题", "降低货损的包装规格选择"],
            "sales_points": ["先确认产品重量、尺寸和运输距离。", "让客户提供样品或装箱方式，再判断纸板层数。", "报价前必须确认印刷、唛头和出口要求。"],
        },
        "fitness_equipment": {
            "category": "健身器材与力量训练产品",
            "selling_points": [
                ("结构稳定", "健身器材客户关注安全、承重和长期使用体验。"),
                ("OEM/ODM 定制", "经销商和跨境卖家需要颜色、包装、规格差异化。"),
                ("场景展示强", "适合用居家训练、健身房陈列和团购场景做内容。"),
            ],
            "segments": [
                ("健身房", "关注耐用、安全、空间利用和补货稳定。", ["老板", "采购", "运营"], ["门店升级", "器械补充", "私教课程更新"]),
                ("经销商", "关注利润空间、SKU 组合和供货稳定。", ["老板", "采购"], ["新品铺货", "旺季备货", "寻找工厂源头"]),
                ("跨境卖家", "关注包装体积、差异化卖点和平台素材。", ["运营", "采购", "老板"], ["新品选品", "Listing 更新", "评价差异化"]),
                ("团购客户", "关注预算、批量交付和售后。", ["行政", "采购", "老板"], ["企业福利", "活动采购", "健身房开业"]),
            ],
            "scenarios": ["家用力量训练", "商用健身房配置", "跨境电商选品", "企业团购福利"],
            "xiaohongshu": ["家用哑铃怎么选不占空间", "健身房器材采购避坑", "包胶哑铃和普通哑铃的区别"],
            "douyin": ["10 秒展示可调节哑铃结构", "健身房开业器材清单", "跨境健身器材拍摄脚本"],
            "wechat": ["健身器材批量采购清单", "经销商选品建议", "家用健身器材 OEM 定制说明"],
            "sales_points": ["先确认使用场景、承重需求和目标价位。", "跨境客户需确认包装体积和平台素材。", "商用客户要重点确认售后、批量交付和安全说明。"],
        },
        "electronics_parts": {
            "category": "电子配件与连接组件",
            "selling_points": [
                ("规格匹配", "电子配件采购首先关注尺寸、接口、线规和兼容性。"),
                ("打样速度", "品牌商和电子厂常先小批量验证，再进入量产。"),
                ("定制生产", "线束、连接件和充电配件通常需要按图纸或样品定制。"),
            ],
            "segments": [
                ("电子厂", "关注规格稳定、交期和批量一致性。", ["采购", "工程", "生产主管"], ["新品量产", "替换供应商", "BOM 降本"]),
                ("品牌商", "关注认证、外观、可靠性和定制能力。", ["产品经理", "采购", "老板"], ["新品开发", "售后问题", "供应链备选"]),
                ("跨境卖家", "关注小批量、包装、上新速度和素材。", ["运营", "采购", "老板"], ["新品测试", "平台上新", "差评改善"]),
                ("维修渠道", "关注常用型号、补货速度和性价比。", ["老板", "采购"], ["高频维修件缺货", "型号替换", "备货"]),
            ],
            "scenarios": ["电子产品组装", "新品打样", "维修替换件补货", "跨境配件上新"],
            "xiaohongshu": ["线束打样前要准备哪些资料", "电子连接件采购怎么避免规格错", "充电配件定制要确认的参数"],
            "douyin": ["30 秒看懂线束打样流程", "连接件规格确认清单", "电子配件小批量生产现场"],
            "wechat": ["电子连接件询价模板", "线束打样资料清单", "电子配件供应商筛选建议"],
            "sales_points": ["先确认图纸、样品、线规、接口和使用场景。", "量产前建议安排样品验证和小批量试产。", "涉及认证和品牌适配时必须人工复核，不做绝对承诺。"],
        },
        "generic_manufacturing": {
            "category": "制造业定制产品",
            "selling_points": [
                ("按需定制", "制造业客户通常需要按规格、图纸或样品确认方案。"),
                ("批量交付", "采购方关注交期、稳定供货和质量复核。"),
                ("工厂直供", "适合强调沟通效率、打样和售后响应。"),
            ],
            "segments": [
                ("中小品牌商", "关注定制能力、打样和稳定交付。", ["老板", "采购", "产品经理"], ["新品开发", "供应商备选"]),
                ("渠道商", "关注价格、交期和可复制素材。", ["老板", "采购", "运营"], ["旺季备货", "新品铺货"]),
            ],
            "scenarios": ["新品开发", "批量采购", "供应商替换", "定制打样"],
            "xiaohongshu": ["工厂定制前要准备哪些资料", "找工厂打样避坑清单", "采购如何判断工厂是否靠谱"],
            "douyin": ["工厂打样流程展示", "定制产品生产现场", "采购问得最多的 3 个问题"],
            "wechat": ["制造业采购资料清单", "工厂定制流程说明", "供应商筛选建议"],
            "sales_points": ["先确认规格、数量、交期和使用场景。", "报价前必须补齐图纸或样品信息。", "涉及认证、客户案例和交付承诺必须人工确认。"],
        },
    }
    return rules.get(category, rules["generic_manufacturing"])


def selling_points(rule: dict[str, Any], payload: dict[str, Any], platforms: list[str]) -> list[dict[str, Any]]:
    capabilities = normalize_list(payload.get("factory_capabilities"))
    evidence_prefix = "；".join(capabilities[:3]) if capabilities else ""
    result = []
    for point, evidence in rule["selling_points"]:
        result.append(
            {
                "point": point,
                "evidence": f"{evidence_prefix}；{evidence}" if evidence_prefix else evidence,
                "suitable_platform": platforms,
            }
        )
    return result


def customer_segments(rule: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "segment": segment,
            "why_fit": why_fit,
            "decision_makers": makers,
            "buying_triggers": triggers,
        }
        for segment, why_fit, makers, triggers in rule["segments"]
    ]


def analyze_product_materials(payload: dict[str, Any]) -> dict[str, Any]:
    payload = payload or {}
    category = infer_category(payload)
    rule = category_rules(category)
    platforms = normalize_list(payload.get("platforms")) or DEFAULT_PLATFORMS
    product_name = str(payload.get("product_name") or payload.get("product") or "制造业产品").strip()
    factory_type = str(payload.get("factory_type") or payload.get("industry") or "制造业工厂").strip()
    location = str(payload.get("company_location") or payload.get("city") or "东莞").strip()
    materials = normalize_list(payload.get("materials"))
    specs = normalize_list(payload.get("specifications"))
    certifications = normalize_list(payload.get("certifications"))
    delivery = str(payload.get("delivery_cycle") or "").strip()
    typical_customers = normalize_list(payload.get("typical_customers") or payload.get("target_customers") or payload.get("target_customer_hint"))
    segments = customer_segments(rule)
    missing = missing_information(payload)

    profile = {
        "product_name": product_name,
        "factory_type": factory_type,
        "location": location,
        "category": rule["category"],
        "summary": str(payload.get("product_description") or f"{location}{factory_type}提供{product_name}，需要补充更多产品资料后用于正式宣传。").strip(),
        "main_specs": specs,
        "materials": materials,
        "certifications": certifications,
        "delivery_notes": delivery or "unknown",
    }

    target_segments = typical_customers or [item["segment"] for item in segments]
    return {
        "skill": "product_intelligence",
        "mode": "draft_only",
        "product_profile": profile,
        "selling_points": selling_points(rule, payload, platforms),
        "suitable_customer_segments": segments,
        "application_scenarios": rule["scenarios"],
        "content_angles": {
            "xiaohongshu": rule["xiaohongshu"],
            "douyin": rule["douyin"],
            "wechat_official_account": rule["wechat"],
        },
        "sales_talking_points": rule["sales_points"],
        "missing_information": missing,
        "risk_notes": [
            "所有内容为 draft_only 草稿，不能自动发布、评论、私信或发邮件。",
            "涉及认证、价格、交期、客户案例和合作品牌时必须人工确认。",
            *missing,
        ],
        "next_growth_inputs": {
            "product_name": product_name,
            "factory_type": factory_type,
            "company_location": location,
            "target_customers": target_segments,
            "target_customer_hint": target_segments,
            "recommended_keywords": [
                f"{location} {factory_type} {product_name}",
                f"{product_name} 采购",
                f"{product_name} 工厂 定制",
                f"{product_name} 小红书 抖音 内容获客",
            ],
            "platforms": platforms,
            "mode": "draft_only",
            "product_profile": profile,
            "product_intelligence": True,
        },
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_product_card(output: dict[str, Any]) -> str:
    profile = output["product_profile"]
    lines = [
        f"# {profile['product_name']} 产品资料卡",
        "",
        "## 产品资料卡",
        "",
        f"- 地区：{profile['location']}",
        f"- 工厂类型：{profile['factory_type']}",
        f"- 产品分类：{profile['category']}",
        f"- 产品摘要：{profile['summary']}",
        f"- 主要规格：{'、'.join(profile['main_specs']) if profile['main_specs'] else '待补充'}",
        f"- 材料：{'、'.join(profile['materials']) if profile['materials'] else '待补充'}",
        f"- 认证：{'、'.join(profile['certifications']) if profile['certifications'] else '待补充'}",
        f"- 交期：{profile['delivery_notes']}",
        "",
        "## 核心卖点",
    ]
    for item in output["selling_points"]:
        lines.append(f"- {item['point']}：{item['evidence']}")
    lines.extend(["", "## 适合客户"])
    for item in output["suitable_customer_segments"]:
        makers = "、".join(item["decision_makers"])
        triggers = "、".join(item["buying_triggers"])
        lines.append(f"- {item['segment']}：{item['why_fit']}；决策人：{makers}；触发点：{triggers}")
    lines.extend(["", "## 内容宣传角度", ""])
    for platform, angles in output["content_angles"].items():
        lines.append(f"### {platform}")
        for angle in angles:
            lines.append(f"- {angle}")
    lines.extend(["", "## 需要补充的信息"])
    for item in output["missing_information"] or ["暂无明显缺失。"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 安全声明", "", "本资料卡为 draft_only 草稿，不真实发布、不评论、不私信、不发邮件。"])
    return "\n".join(lines) + "\n"


def build_summary(output: dict[str, Any]) -> str:
    profile = output["product_profile"]
    missing_count = len(output["missing_information"])
    segment_names = "、".join(item["segment"] for item in output["suitable_customer_segments"][:4])
    point_names = "、".join(item["point"] for item in output["selling_points"][:3])
    return (
        f"# {profile['product_name']} 产品理解摘要\n\n"
        f"- 产品分类：{profile['category']}\n"
        f"- 核心卖点：{point_names}\n"
        f"- 适合客户：{segment_names}\n"
        f"- 需要补充信息数量：{missing_count}\n"
        f"- 模式：draft_only\n"
    )


def write_case_outputs(output_dir: str | Path, output: dict[str, Any]) -> dict[str, str]:
    output_dir = Path(output_dir)
    growth_input = dict(output["next_growth_inputs"])
    growth_input["product_profile"] = output["product_profile"]
    growth_input["product_intelligence_output"] = output
    growth_input["mode"] = "draft_only"

    paths = {
        "product_profile": output_dir / "product_profile.json",
        "product_card": output_dir / "product_card.md",
        "growth_input": output_dir / "growth_input.json",
        "summary": output_dir / "product_understanding_summary.md",
    }
    write_json(paths["product_profile"], output["product_profile"])
    write_text(paths["product_card"], build_product_card(output))
    write_json(paths["growth_input"], growth_input)
    write_text(paths["summary"], build_summary(output))
    return {key: str(value) for key, value in paths.items()}


def read_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.input_json:
        return json.loads(args.input_json)
    if args.input_file:
        return json.loads(Path(args.input_file).read_text(encoding="utf-8-sig"))
    raise ValueError("需要提供 --input-file 或 --input-json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="宇智能产品资料理解 Skill")
    parser.add_argument("--input-file", default="")
    parser.add_argument("--input-json", default="")
    parser.add_argument("--output-file", default="")
    parser.add_argument("--output-dir", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output = analyze_product_materials(read_payload(args))
        if args.output_dir:
            output["generated_files"] = write_case_outputs(args.output_dir, output)
        text = json.dumps(output, ensure_ascii=False, indent=2)
        if args.output_file:
            Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output_file).write_text(text + "\n", encoding="utf-8", newline="\n")
        else:
            print(text)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
