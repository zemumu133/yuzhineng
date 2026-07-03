# Phase 1A-CommercialSurfaceAudit：LobsterAI 商业化暴露面审计

测试日期：2026-06-30  
项目名称：宇智能  
审计对象：`D:\OpenClaw\v2\client-shell\lobsterai\src`  
审计性质：只审计，不做完整白标改造，不连接真实账号，不读取 secrets，不真实外发。

## 一、总体结论

LobsterAI 可以作为“宇智能”桌面客户端底座继续验证，但当前上游版本不适合直接白标发布。原因不是单纯 Logo 或名称问题，而是桌面端深度绑定了 LobsterAI / 网易有道的登录、服务协议、Portal、更新、遥测、模型服务、技能商店、部分 IM 通道和 Computer Use 资源。

结论：继续 LobsterAI，但下一阶段必须先做“最小白标隔离层”，再谈对外试用或商业交付。

## 二、白标化可行性判断

- 能否白标化：可以。
- 是否只是换名称和图标：不是。
- 最小白标改造范围：应用身份、欢迎页、About、协议隐私、官方登录、官方 Portal、官方模型服务、自动更新、遥测、官方商店、网易系 IM 通道、打包配置、开源许可证声明。
- 必须替换的上游依赖：LobsterAI 官方账号体系、`lobsterai-server*.youdao.com`、`lobsterai.youdao.com/portal`、Overmind 更新/登录/商店接口、`rlogs.youdao.com`、网易/有道协议 URL、POPO/NIM/Bee/ClawEmail 等网易系通道。
- 必须保留的开源声明：MIT License 中的 `Copyright (c) 2026 NetEase Youdao`，OpenClaw 及第三方依赖许可证，随包 SKILLs 中的专有或第三方 LICENSE。
- 是否适合继续作为“宇智能”的桌面底座：适合继续 PoC 和内部开发；不适合不加隔离地对外商用。

## 三、暴露项清单

### 1. 应用包名与作者信息

- 暴露项名称：`package.json` 应用元信息。
- 文件路径：`D:\OpenClaw\v2\client-shell\lobsterai\src\package.json`
- 当前内容：`name = lobsterai`，`author.name = LobsterAI`，`author.email = lobsterai.project@rd.netease.com`，`license = MIT`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：将包名改为 `yuzhineng` 或 `yu-intelligence`，作者信息改为宇智能项目主体；保留 MIT 许可证字段和上游许可证文件。
- 是否涉及法律/许可证保留：涉及。MIT 许可证和上游版权声明必须保留。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 2. Electron 打包身份

- 暴露项名称：`productName`、`appId`、可执行文件名、协议名。
- 文件路径：`D:\OpenClaw\v2\client-shell\lobsterai\src\electron-builder.json`
- 当前内容：`appId = com.lobsterai.app`，`productName = LobsterAI`，`executableName = LobsterAI`，协议 `lobsterai://`，macOS 权限文案中多处 `LobsterAI`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：改为 `com.yuzhineng.app`、`宇智能`、`Yuzhineng`、`yuzhineng://`；权限文案改为宇智能。
- 是否涉及法律/许可证保留：不直接涉及许可证，但涉及品牌与系统注册身份。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 3. HTML 标题

- 暴露项名称：应用窗口 HTML title。
- 文件路径：`D:\OpenClaw\v2\client-shell\lobsterai\src\index.html`
- 当前内容：`<title>LobsterAI</title>`。
- 商业化风险等级：中。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：改为 `<title>宇智能</title>`。
- 是否涉及法律/许可证保留：否。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 4. 主进程应用常量

- 暴露项名称：应用名称、应用 ID、Windows AppUserModelID、本地数据库文件名。
- 文件路径：`D:\OpenClaw\v2\client-shell\lobsterai\src\src\main\appConstants.ts`
- 当前内容：`APP_NAME = LobsterAI`，`APP_ID = lobsterai`，`APP_USER_MODEL_ID = com.lobsterai.app`，`DB_FILENAME = lobsterai.sqlite`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：改为 `宇智能`、`yuzhineng`、`com.yuzhineng.app`、`yuzhineng.sqlite`，同时设计旧数据迁移或新白标版本隔离策略。
- 是否涉及法律/许可证保留：否。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 5. 渲染层应用名称常量

- 暴露项名称：前端显示用 APP_NAME。
- 文件路径：`D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\constants\app.ts`
- 当前内容：`APP_NAME = LobsterAI`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：改为 `宇智能`，并统一由一个品牌配置文件导出，避免多处硬编码。
- 是否涉及法律/许可证保留：否。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 6. 欢迎页与核心界面品牌

- 暴露项名称：欢迎页、Cowork 视图、启动遮罩中的 LobsterAI 品牌。
- 文件路径：`src\renderer\components\WelcomeDialog.tsx`、`src\renderer\components\cowork\CoworkView.tsx`、`src\renderer\components\cowork\EngineStartupOverlay.tsx`、`src\renderer\components\cowork\CoworkSessionDetail.tsx`
- 当前内容：Logo 的 `alt = LobsterAI`，界面标题和分享图中出现 `LobsterAI`、`LobsterAI — 全场景个人助理 Agent`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：统一改为宇智能品牌文案，例如“宇智能 - AI 获客与内容运营助手”。
- 是否涉及法律/许可证保留：否。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 7. Logo、托盘图标与安装图标

- 暴露项名称：Logo 和图标资源。
- 文件路径：`public\logo.png`、`resources\tray\*`、`build\icons\*`
- 当前内容：使用 LobsterAI 上游 Logo / 图标资源。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：生成宇智能正式图标，并同步替换窗口图标、托盘图标、安装包图标、About 页图标。
- 是否涉及法律/许可证保留：可能涉及商标/视觉版权，建议替换。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 8. 服务协议与隐私弹窗

- 暴露项名称：服务协议 / 隐私政策链接与文案。
- 文件路径：`src\renderer\components\PrivacyDialog.tsx`、`src\renderer\services\i18n.ts`
- 当前内容：协议 URL 指向 `https://c.youdao.com/dict/hardware/lobsterai/lobsterai_service.html`；中文文案为“网易有道LobsterAI服务协议”；英文文案为“NetEase Youdao LobsterAI Terms of Service”。
- 商业化风险等级：严重。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：使用宇智能自己的服务协议、隐私政策和本地/官网链接；首次启动弹窗改为宇智能协议。
- 是否涉及法律/许可证保留：涉及。不能把网易有道协议当作宇智能协议使用；开源许可证声明需另行保留。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 9. About 页面

- 暴露项名称：About 页品牌、官网、用户手册、社区、版权。
- 文件路径：`src\renderer\components\Settings.tsx`
- 当前内容：`ABOUT_USER_MANUAL_URL = https://lobsterai.youdao.com/#/docs/lobsterai_user_manual`，`ABOUT_USER_COMMUNITY_URL = https://lobsterai.youdao.com/#/about`，`ABOUT_SERVICE_TERMS_URL = https://c.youdao.com/.../lobsterai_service.html`，页面显示 `LobsterAI`，版权为 `NetEase Youdao. All Rights Reserved.`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：改为宇智能手册、官网/社区、宇智能协议和宇智能版权，同时新增“开源许可证”入口保留上游声明。
- 是否涉及法律/许可证保留：涉及。不能删除上游 MIT 声明，但 About 的商业版权不能继续显示网易有道为产品主体。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 10. 官方登录入口

- 暴露项名称：LobsterAI / 有道 Portal 登录。
- 文件路径：`src\renderer\services\endpoints.ts`、`src\renderer\services\auth.ts`、`src\renderer\components\LoginButton.tsx`
- 当前内容：登录 URL 来自 `api-overmind.youdao.com/.../lobsterai/.../login-url`，兜底跳转 `https://lobsterai.youdao.com/portal#/login`，登录按钮会打开 Profile、Recharge、Invitation 等 Portal 页面。
- 商业化风险等级：严重。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版先关闭官方登录，改为本地模式 + 用户自填 DeepSeek Key；商业版再接宇智能账号系统。
- 是否涉及法律/许可证保留：不直接涉及许可证，但涉及账号、支付、隐私和用户数据主体。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 11. 官方 token、用户资料与配额模型

- 暴露项名称：Token、用户资料、订阅、余额、模型配额。
- 文件路径：`src\main\preload.ts`、`src\renderer\store\slices\authSlice.ts`、`src\main\authQuota.ts`、`src\renderer\services\auth.ts`
- 当前内容：暴露 `auth:login`、`auth:exchange`、`auth:getUser`、`auth:getQuota`、`auth:refreshToken`、`auth:getAccessToken`、`auth:getModels` 等 IPC；UI 展示计划、余额和免费额度。
- 商业化风险等级：严重。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版移除或隐藏上游账号/配额 UI；后续接自有账号与计费系统。
- 是否涉及法律/许可证保留：涉及隐私和数据处理边界。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 12. 官方 Server API

- 暴露项名称：LobsterAI 官方后端 API。
- 文件路径：`src\main\libs\endpoints.ts`
- 当前内容：`https://lobsterai-server.inner.youdao.com` 与 `https://lobsterai-server.youdao.com`，用于 auth exchange/refresh、models、proxy、html share 等。
- 商业化风险等级：严重。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版禁用官方 Server API；保留本地模式和用户自有模型 Key；需要云功能时接宇智能后端。
- 是否涉及法律/许可证保留：涉及用户数据与第三方服务调用合规。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 13. 官方模型 Provider

- 暴露项名称：`lobsterai-server`、`lobsterai-copilot`、`lobster` 等官方模型 provider。
- 文件路径：`src\shared\providers\constants.ts`、`src\renderer\services\auth.ts`
- 当前内容：Provider 中包含 `LobsteraiServer`、`LobsteraiCopilot`、`Lobster`；服务端模型目录会从 LobsterAI 官方账号体系加载。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版隐藏官方模型服务，默认使用 DeepSeek / OpenAI-compatible / 本地可配置 provider；宇智能模型聚合服务后置。
- 是否涉及法律/许可证保留：不直接涉及许可证，但涉及模型服务品牌和计费主体。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 14. DeepSeek 与通用 Provider 列表

- 暴露项名称：第三方模型 Provider 列表。
- 文件路径：`src\shared\providers\constants.ts`
- 当前内容：已包含 DeepSeek V4 Flash / Pro / Reasoner 等定义，也包含 Youdao provider。
- 商业化风险等级：中。
- 是否必须替换：部分必须。
- 建议替换为“宇智能”的方案：保留 DeepSeek、OpenAI-compatible 等通用 provider；隐藏或移除 Youdao / LobsterAI 官方 provider。
- 是否涉及法律/许可证保留：第三方 provider 名称可作为配置项保留，但不能误导为宇智能自有服务。
- 是否建议第一版修改：是，至少隐藏 LobsterAI/Youdao 默认项。
- 是否可以延后：Youdao provider 可延后清理，但不能作为默认服务。

### 15. 自动更新服务

- 暴露项名称：官方自动更新、手动更新和下载页。
- 文件路径：`src\main\libs\endpoints.ts`、`src\renderer\services\endpoints.ts`、`src\main\libs\appUpdateCoordinator.ts`
- 当前内容：更新接口指向 `api-overmind.youdao.com/openapi/get/luna/hardware/lobsterai/.../update`，下载页指向 `lobsterai.youdao.com/#/download-list`。
- 商业化风险等级：严重。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版禁用自动更新；打包发布前改为宇智能自己的更新源或手动下载页。
- 是否涉及法律/许可证保留：不直接涉及许可证，但涉及供应链安全。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 16. Skill / Kit 官方商店

- 暴露项名称：LobsterAI Skill Store / Kit Store。
- 文件路径：`src\main\libs\endpoints.ts`、`src\renderer\services\endpoints.ts`
- 当前内容：商店接口指向 `api-overmind.youdao.com/openapi/get/luna/hardware/lobsterai/.../skill-store` 与 `.../kit-store`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版关闭官方商店入口，只启用本地内置获客 Skill；后续建设宇智能模板市场。
- 是否涉及法律/许可证保留：涉及第三方 Skill 许可证和分发合规。
- 是否建议第一版修改：是。
- 是否可以延后：否，至少要隐藏入口。

### 17. 遥测与日志上报

- 暴露项名称：Youdao Analyzer 事件上报。
- 文件路径：`src\renderer\services\logReporter.ts`、`src\renderer\services\i18n.ts`
- 当前内容：上报到 `https://rlogs.youdao.com/rlog.php`；事件前缀为 `lobsterai_`；产品参数为 `wisdom`；文案为“帮助改进 LobsterAI”。
- 商业化风险等级：严重。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版默认关闭遥测；如需统计，后续接宇智能自有匿名遥测并提供开关和隐私说明。
- 是否涉及法律/许可证保留：涉及隐私合规。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 18. Portal、价格、充值、邀请入口

- 暴露项名称：官方会员和付费入口。
- 文件路径：`src\renderer\components\LoginButton.tsx`、`src\renderer\services\endpoints.ts`、`src\renderer\services\i18n.ts`
- 当前内容：用户菜单跳转 Profile、Recharge、Invitation、Pricing；部分文案引用 LobsterAI Portal。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版隐藏会员、充值、邀请入口；商业计费系统后置到宇智能账户体系。
- 是否涉及法律/许可证保留：涉及交易主体与用户协议。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 19. 官方网站与文档链接

- 暴露项名称：官网、用户手册、IM 配置文档。
- 文件路径：`src\renderer\components\Settings.tsx`、`src\shared\platform\constants.ts`
- 当前内容：多个链接指向 `https://lobsterai.youdao.com/#/docs/...`、`https://lobsterai.youdao.com/#/about`。
- 商业化风险等级：中。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版改为本地说明文档或宇智能文档站；无法提供文档时隐藏入口。
- 是否涉及法律/许可证保留：否。
- 是否建议第一版修改：是。
- 是否可以延后：部分深层配置文档可延后，但首页/About 暴露不可延后。

### 20. 网易 / POPO / NIM / Bee 通道

- 暴露项名称：网易系 IM 与企业通道。
- 文件路径：`package.json`、`src\main\im\imGatewayManager.ts`、`src\shared\im\nimQrLogin.ts`、`src\shared\platform\constants.ts`
- 当前内容：插件包含 `moltbot-popo`、`openclaw-nim-channel`、`openclaw-netease-bee`；代码含 `open.popo.netease.com`、`lbs.netease.im`、网易 Bee 平台定义。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版隐藏/禁用网易系通道；只保留用户明确需要且可合法配置的通用通道。
- 是否涉及法律/许可证保留：可能涉及第三方 SDK/平台条款。
- 是否建议第一版修改：是。
- 是否可以延后：不能暴露给普通用户；底层代码可后续清理。

### 21. ClawEmail / 内部邮件授权

- 暴露项名称：Claw 邮件授权与 API Key 页面。
- 文件路径：`src\renderer\components\im\IMSettings.tsx`、`src\main\im\imGatewayManager.ts`
- 当前内容：跳转 `https://claw.163.com/projects/dashboard/?channel=LobsterAI#/api-keys`；邮件 token endpoint 为 `https://claw.163.com/claw-api-gateway/open/v1/mail/auth/im-token`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版隐藏 ClawEmail；邮件草稿与人工发送保留在本地工作流中。
- 是否涉及法律/许可证保留：涉及邮件服务条款和用户授权。
- 是否建议第一版修改：是。
- 是否可以延后：否，至少隐藏入口。

### 22. Computer Use 下载资源与提示

- 暴露项名称：Computer Use runtime / kit 下载与品牌提示。
- 文件路径：`src\main\computerUse\computerUseRuntime.ts`、`src\main\computerUse\computerUseKit.ts`、`src\shared\computerUse\constants.ts`
- 当前内容：下载地址指向网易 NOS 资源；文件名包含 `lobsterai-computer-use-runtime`；提示文案出现 `LobsterAI正在使用你的电脑`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：第一版禁用 Computer Use 自动下载；需要时改为宇智能自托管资源和宇智能权限提示。
- 是否涉及法律/许可证保留：可能涉及二进制分发许可证和安全告知。
- 是否建议第一版修改：是。
- 是否可以延后：不能作为默认开启能力。

### 23. 国际化文案中的品牌

- 暴露项名称：中英文 i18n 文案。
- 文件路径：`src\renderer\services\i18n.ts`、`src\main\i18n.ts`
- 当前内容：大量 `LobsterAI`、`网易有道`、`NetEase Youdao`、Portal、官方站点、升级、权限、备份等文案。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：建立品牌词表，集中替换可见文案；法律/开源声明类文案单独保留。
- 是否涉及法律/许可证保留：部分涉及，不能把许可证和版权声明简单替换掉。
- 是否建议第一版修改：是。
- 是否可以延后：普通用户可见文案不可延后；开发者文档可延后。

### 24. README 与上游项目说明

- 暴露项名称：README / README_zh 中的上游介绍。
- 文件路径：`README.md`、`README_zh.md`
- 当前内容：描述 LobsterAI 为网易有道出品的开源桌面级 Agent，并链接 Youdao 和 LICENSE。
- 商业化风险等级：中。
- 是否必须替换：部分必须。
- 建议替换为“宇智能”的方案：产品分发包中使用宇智能 README；保留第三方开源声明中的上游来源和许可证。
- 是否涉及法律/许可证保留：涉及，上游来源不能抹掉。
- 是否建议第一版修改：是，至少新增宇智能 README 和开源声明。
- 是否可以延后：对外分发前不可延后；内部 PoC 可延后。

### 25. 开源许可证与第三方许可证

- 暴露项名称：上游 MIT License、SKILLs 许可证、第三方依赖许可证。
- 文件路径：`LICENSE`、`SKILLs\**\LICENSE.txt`、`SKILLs\**\SKILL.md`
- 当前内容：根许可证为 MIT，版权为 `Copyright (c) 2026 NetEase Youdao`；部分 SKILL 标注 Proprietary 或 Apache/MIT/OFL 等。
- 商业化风险等级：严重。
- 是否必须替换：不能替换为删除；必须保留并补充宇智能自己的声明。
- 建议替换为“宇智能”的方案：新增“开源许可证与第三方声明”页面/文档；保留上游 MIT 和第三方 LICENSE；宇智能自有代码另加版权声明。
- 是否涉及法律/许可证保留：强相关，必须保留。
- 是否建议第一版修改：是。
- 是否可以延后：否。

### 26. 打包排除许可证文件的配置

- 暴露项名称：打包时排除 LICENSE 文件。
- 文件路径：`electron-builder.json`
- 当前内容：`files` 和 SKILLs 过滤规则中排除了 `LICENSE`、`LICENSE.md`、`LICENSE.txt`。
- 商业化风险等级：高。
- 是否必须替换：是。
- 建议替换为“宇智能”的方案：打包时附带统一的 `THIRD_PARTY_NOTICES` 或“开源许可证”页面，不直接把必要许可证文件排除在发行包外。
- 是否涉及法律/许可证保留：强相关。
- 是否建议第一版修改：是。
- 是否可以延后：否。

## 四、最小白标改造范围

第一版白标隔离建议只做必要改造，不做完整品牌化大工程：

1. 建立 `brand` 配置层：产品名、英文名、协议名、官网、支持邮箱、版权主体、更新源、隐私协议 URL。
2. 替换应用身份：`package.json`、`electron-builder.json`、`appConstants.ts`、`index.html`、图标资源。
3. 替换普通用户可见文案：欢迎页、About、服务协议、隐私弹窗、更新提示、登录入口、会员入口。
4. 禁用上游账号体系：隐藏登录、充值、邀请、官方 token、官方配额、官方模型目录。
5. 禁用或改造外联服务：自动更新、遥测、Skill/Kit 商店、官方 Portal、官方文档链接。
6. 隐藏网易系通道：POPO、NIM、Bee、ClawEmail。
7. 保留可独立使用的能力：本地 OpenClaw runtime、DeepSeek/OpenAI-compatible provider、本地 Skill、手动配置模型。
8. 新增开源许可证声明：保留 NetEase Youdao MIT、OpenClaw、SKILLs 和第三方依赖声明。

## 五、必须替换的上游依赖

- LobsterAI 官方账号/Portal：`lobsterai.youdao.com/portal`
- LobsterAI 官方 Server API：`lobsterai-server.youdao.com`、`lobsterai-server.inner.youdao.com`
- Overmind 更新/登录/商店接口：`api-overmind.youdao.com/openapi/get/luna/hardware/lobsterai/...`
- Youdao 遥测：`rlogs.youdao.com`
- 网易有道服务协议链接：`c.youdao.com/dict/hardware/lobsterai/lobsterai_service.html`
- 网易系 IM：POPO、NIM、NetEase Bee
- ClawEmail：`claw.163.com`
- Computer Use 网易 NOS 下载资源
- LobsterAI 图标、品牌名、协议名、安装包标识

## 六、可以保留但需隔离的能力

- OpenClaw runtime：可以保留，但要与宇智能本地数据目录、日志、配置隔离。
- DeepSeek provider：可以保留并作为宇智能默认模型配置入口。
- OpenAI-compatible provider：可以保留。
- 本地 Skill / MCP / CLI 调用：可以保留，适合宇智能获客工作流。
- 通用 IM 插件：只有在用户主动配置、合法授权、且不自动外发时才保留。

## 七、第一版建议修改

第一版建议优先完成以下事项：

1. 替换应用身份、图标、窗口标题和 About 页。
2. 替换服务协议/隐私链接，新增宇智能协议占位页。
3. 默认关闭官方登录、官方 Portal、充值、邀请和会员入口。
4. 默认关闭官方自动更新和遥测。
5. 隐藏 LobsterAI Server / Youdao 模型 provider。
6. 隐藏网易系 IM 和 ClawEmail。
7. 新增“开源许可证与第三方声明”页面或文档。
8. 保持 DeepSeek 与本地 Skill 路线可用。

## 八、可以延后的事项

- 完整 UI 品牌视觉系统。
- 自有账号体系和计费系统。
- 自有更新服务。
- 自有 Skill/模板市场。
- 完整官网与帮助中心。
- 打包签名、公证、自动升级链路。
- 深层开发文档中的 LobsterAI 历史引用清理。

## 九、门禁判断

- 当前版本允许继续内部 PoC：允许。
- 当前版本允许给内部团队演示：条件允许，演示前需说明仍是上游壳验证。
- 当前版本允许对客户试用：不建议。
- 当前版本允许商业发布：不允许。
- 进入下一阶段建议：进入 Phase 1A-WhiteLabelMVP，先做最小白标隔离和官方服务禁用。

## 十、已执行检查

- 运行 `D:\OpenClaw\v2\scripts\v2-task-precheck.ps1`。
- 使用 `rg` 检查 LobsterAI / NetEase / Youdao / 官方链接 / license / About / openExternal / provider / update / analytics 暴露点。
- 读取关键文件片段：`package.json`、`electron-builder.json`、`src\main\libs\endpoints.ts`、`src\renderer\services\endpoints.ts`、`src\renderer\services\logReporter.ts`、`src\main\appConstants.ts`、`src\renderer\components\Settings.tsx`。
- 未读取 `D:\OpenClaw\secrets`。
- 未连接真实账号。
- 未发送邮件、私信、评论或发帖。
- 未修改旧 console。

