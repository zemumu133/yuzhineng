# product_intelligence MVP

`product_intelligence` 是“宇智能”的产品资料理解 Skill。它先理解工厂产品，再把结果交给 `domestic_signal_growth` 做商机发掘、内容草稿和销售交接。

## 当前能力

- 提炼产品基础信息、卖点、适合客户、应用场景、采购决策人。
- 生成小红书、抖音、公众号内容角度。
- 生成销售跟进重点和需要补充的信息。
- 生成可被 `domestic_signal_growth` 直接使用的 `growth_input.json`。
- 全程 `draft_only`，不真实发布、不评论、不私信、不发邮件。

## PowerShell 调用

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\OpenClaw\v2\skills\product_intelligence\product_intelligence.ps1" -InputFile "D:\OpenClaw\v2\skills\product_intelligence\examples\heavy_packaging_product.json" -OutputDir "D:\OpenClaw\v2\test-cases\product_intelligence\heavy_packaging"
```

## 输出文件

使用 `-OutputDir` 时会生成：

- `product_profile.json`
- `product_card.md`
- `growth_input.json`
- `product_understanding_summary.md`

## 安全边界

本 Skill 不读取 secrets，不调用社媒账号，不发送任何外部动作，不采集私人联系方式，不绕过验证码、登录墙或平台限制。
