# Phase 1A-CapabilityFirst：LobsterAI / OpenClaw 能力优先验证报告

测试日期：2026-07-01  
项目名称：宇智能  
测试范围：LobsterAI + OpenClaw runtime + DeepSeek provider + 内置 Skill + 专家套件目录 + 本地 `domestic_signal_growth` 占位 Skill  
测试原则：不白标化、不登录新账号、不读取 secrets、不真实外发、不连接真实社媒账号、不提交构建产物。

## 1. 当前 LobsterAI commit

- LobsterAI 上游仓库：`https://github.com/netease-youdao/LobsterAI`
- 源码获取方式：Phase 1A-Fast 使用官方 main 分支 zip 包，非 `.git` 工作树。
- 记录的 LobsterAI commit：`b2317e65785ec02e982895c98c4c82d36d37d5f0`
- 当前 v2 治理基线 commit：`313ba9954d101d902246a14cbce43dbbb706ae4b`

## 2. OpenClaw runtime 是否可用

结论：可用。

验证命令：

```powershell
npm run electron:dev:openclaw
```

关键结果：

- OpenClaw source 已在 `v2026.6.1`。
- OpenClaw runtime build 命中缓存，无需重编译。
- OpenClaw patches 已应用。
- Gateway 启动成功。
- 日志出现 `[gateway] ready`。
- Gateway 端口：本次运行分配到 `18790`。

注意事项：

- 可选网易 POPO 插件 `moltbot-popo` 从 `https://npm.nie.netease.com` 拉取时出现 `ECONNRESET`，但脚本将其视为 optional 并继续。
- Gateway 启动时提示安全风险：`browser.ssrfPolicy.dangerouslyAllowPrivateNetwork=true`。后续能力产品化前必须处理。

## 3. Cowork mode 是否可用

结论：基础可用。

观察到的启动结果：

- Electron UI 启动成功。
- CoworkProxy 启动成功。
- `IMGatewayManager` 创建 Cowork handler。
- OpenClaw gateway 被 Cowork 流程拉起并进入 ready。
- Web Search Bridge Server 启动成功。

限制：

- 本轮未通过 UI 对话框提交完整 Cowork 任务。
- 历史运行中首次启动曾出现服务协议弹窗；本轮日志显示 privacy check 已完成，但未代替用户点击任何协议或登录。
- 本机存在上游账号缓存状态，程序能读取到登录态；本轮没有进行新登录，也不记录账号信息。

## 4. DeepSeek 是否可用

结论：部分可用。

已确认：

- DeepSeek provider 存在。
- `deepseek-v4-flash` 存在。
- `deepseek-v4-pro` 存在。
- OpenClaw gateway 自动识别到 DeepSeek provider。
- Startup config 中 primary model 当前为 `deepseek/deepseek-v4-flash`。
- OpenClaw gateway 日志显示 agent model 为 `deepseek/deepseek-v4-flash`。

未完成：

- 未在 Cowork UI 中完成一次 DeepSeek 简单对话。
- 未把新任务默认模型切到 `deepseek/deepseek-v4-pro`。
- 未验证 Agent / Cowork 在真实任务中一定调用 V4 Pro。

判断：

- DeepSeek provider 接入路线成立。
- 当前默认模型偏向 Flash，不满足“高价值业务任务默认 V4 Pro”的目标。
- 下一步应明确把业务任务模型绑定到 `deepseek/deepseek-v4-pro`，低阶分类再使用 Flash。

## 5. 内置技能测试结果

| 技能 | 是否存在/启用 | 最小测试结果 | 是否需要登录 | 是否依赖官方服务 | 是否本地可用 | 失败原因/备注 |
| --- | --- | --- | --- | --- | --- | --- |
| web-search | 是，默认启用 | 通过。搜索“职业证书培训机构营销方式”，返回 5 条公开网页结果 | 否 | 否，依赖公开搜索引擎和本地 Bridge | 是 | Bridge 健康检查通过，搜索耗时约 1.8s |
| docx | 是，默认启用 | 通过。生成并读取 `capability_docx_test.docx` | 否 | 否 | 是 | 使用本机 Python 文档库完成最小验证；未通过 Cowork UI 调用 |
| xlsx | 是，默认启用 | 通过。生成并读取 `capability_xlsx_test.xlsx` | 否 | 否 | 是 | LobsterAI 源码中存在 `xlsx` Node 依赖；本轮使用 Python `openpyxl` 做最小验证 |
| pdf | 是，默认启用 | 通过。生成并读取 PDF；嵌入中文字体后中文可正常提取 | 否 | 否 | 是 | 默认 PDF 字体会导致中文提取成方块，需固定中文字体策略 |
| pptx | 是，默认启用 | 部分通过。使用 `python-pptx` 成功生成 3 页 PPTX | 否 | 否 | 是 | Node `pptxgenjs` 路径缺少 `jszip`，需要补依赖或统一走 Python/HTML2PPTX |
| playwright / browser | 是，playwright Skill 存在；OpenClaw browser 插件加载 | 部分通过。web-search 的 Playwright Bridge 可搜索公开网页；直接 Playwright 调用失败 | 否 | 否 | 部分 | 直接 Node 调用缺 `playwright-core`；需补 runtime 依赖 |
| command / local-tools | local-tools 存在，默认启用 | 未做危险命令测试 | 否 | 否 | 待验证 | 后续应只验证白名单命令，不开放任意执行给获客 Agent |

测试产物位于忽略目录：

`D:\OpenClaw\workspaces\capability-validation\`

该目录不提交 Git。

## 6. 专家套件测试结果

结论：公开目录可访问，安装未执行。

验证方式：

- 请求官方 Kit Store：`https://api-overmind.youdao.com/openapi/get/luna/hardware/lobsterai/prod/kit-store`
- 返回 `code = 0`。
- 公开目录中存在以下与本项目相关的专家套件：
  - `marketing` / 营销
  - `sales` / 销售
  - `customer-support` / 客户支持
  - `data` / 数据

| 专家套件 | 是否能看到 | 是否安装 | 是否需要登录 | 是否依赖官方市场 | 是否适合后续参考 |
| --- | --- | --- | --- | --- | --- |
| 营销 | 是 | 未安装 | 目录访问未要求登录 | 是 | 是，适合作为内容/活动模板参考 |
| 销售 | 是 | 未安装 | 目录访问未要求登录 | 是 | 是，适合触达草稿、销售漏斗参考 |
| 客户支持 | 是 | 未安装 | 目录访问未要求登录 | 是 | 部分适合，可借鉴客户回复和问题分级 |
| 数据 | 是 | 未安装 | 目录访问未要求登录 | 是 | 是，适合 CRM 分析和报表模板参考 |

未安装原因：

- 安装会下载上游 bundle 到本机，并可能引入未知脚本/依赖。
- 本阶段目标是能力验证，不执行未知专家套件安装。
- 如需安装，应在下一阶段对 bundle 进行许可证、脚本、依赖和安全审查后再做。

## 7. 自然语言创建 Agent 是否可用

结论：部分可用，未完成端到端验证。

已确认：

- LobsterAI 代码中存在自定义 Agent 的 CRUD 能力。
- Agent 支持字段：名称、描述、系统提示词、身份、模型、工作目录、图标、skillIds。
- README 明确说明支持创建专用 Agent。
- Agent 数据存入本地 SQLite 的 `agents` 表。

未完成：

- 未通过 LobsterAI UI 自然语言创建“宇智能获客 Agent”。
- 未验证自然语言能自动转成 Agent 配置。
- 未验证外部动作限制能作为结构化权限固化到 Agent 层。

判断：

- 结构化创建 Agent 的底层能力成立。
- “自然语言创建 Agent”目前更像 UI/LLM 编排层能力，仍需后续验证或开发。
- 外部动作限制目前主要依赖系统提示词、OpenClaw 权限门控和人工审批，不是独立的获客权限卡模型。

## 8. domestic_signal_growth Skill 是否可接入

结论：本地脚本可运行，尚未接入 LobsterAI Skill / MCP / Cowork。

文件：

`D:\OpenClaw\v2\skills\domestic_signal_growth\hello_growth.ps1`

直接运行结果：

```text
国内营销信号穿透 Skill 占位：已接收推广目标，将输出商机判断、客户类型、内容建议和待办。
```

已验证：

- PowerShell 直接运行成功。
- 不读取 secrets。
- 不外发网络请求。
- 不真实发布、私信、评论或发邮件。

未完成：

- 未注册为 LobsterAI `SKILLs` 目录下的正式 Skill。
- 未注册 MCP server。
- 未在 Cowork 中通过自然语言调用。

最小接入路径：

1. 将 `domestic_signal_growth` 做成正式 `SKILL.md + scripts` 目录。
2. 放入 LobsterAI 用户 Skill 目录或通过 Skill Manager 安装。
3. 或封装为 MCP stdio server，让 Cowork/OpenClaw 以工具方式调用。
4. 在 Agent 系统提示词中限制所有外部动作只能输出草稿和待办。

## 9. 最小业务任务是否完成

任务：

“我要推广职业证书考评服务，目标客户是培训机构和人力资源公司。请帮我判断是否有商机，给出目标客户类型、小红书内容建议、抖音内容建议、跟进待办。不要真实发布，不要私信，不要评论，不要发邮件。”

结论：部分完成。

已完成：

- 使用 web-search 搜索公开网页。
- 找到职业教育培训、人力资源职业技能培训、专项职业能力测评、地方培训机构申报等公开线索。
- 生成本地业务任务输出，包括：
  - 商机判断
  - 目标客户类型
  - 公开信息研究摘要
  - 小红书内容建议
  - 抖音内容建议
  - 跟进话术草稿
  - 待办清单
  - 风险提醒
  - 下一步建议

输出文件：

`D:\OpenClaw\workspaces\capability-validation\business_task_result_cn.md`

未完成：

- 未通过 LobsterAI / Cowork / Agent 对话框端到端执行。
- 未验证 DeepSeek V4 Pro 在该任务中的真实调用。
- 未生成正式审批队列。

风险提醒：

- 职业证书、考评、培训宣传必须避免“包过”“保就业”“官方授权”等未经证明的承诺。
- 任何评论、私信、邮件、发布都必须继续保持草稿和人工审批。

## 10. 依赖上游登录/市场的能力

- 上游账号资料、订阅、额度。
- LobsterAI Server 官方模型目录。
- 专家套件安装。
- Skill / Kit 官方市场。
- 自动更新服务。
- 部分 IM / 网易系通道。

本轮没有进行新登录，也没有安装专家套件。

## 11. 可以离线或本地运行的能力

- OpenClaw runtime 本机启动。
- Cowork gateway 本机启动。
- 本地 Skill 脚本直接运行。
- docx / xlsx / pdf / pptx 文件生成。
- Web Search Bridge 本机服务启动，但搜索本身需要公网。
- OpenClaw browser 插件加载。

## 12. 当前是否具备继续做“宇智能获客能力”的基础

结论：具备基础，但尚未形成完整闭环。

已成立的基础：

- 桌面壳可启动。
- OpenClaw runtime 可启动。
- Cowork / gateway 可进入 ready。
- DeepSeek provider 已存在，并可被配置同步识别。
- Web-search 可做公开搜索。
- 文档、表格、PDF、PPTX 输出能力可行。
- 营销/销售/客户支持/数据专家套件在官方目录存在，可作为行业模板参考。

关键阻塞：

1. DeepSeek 业务任务还没有强制绑定 V4 Pro。
2. 本地 `domestic_signal_growth` 还没有正式接入 Cowork / Skill / MCP。
3. 自然语言创建 Agent 未完成端到端验证。
4. 专家套件未安装，安装前需要安全审查。
5. 自动更新在开发启动时会连接上游并下载官方更新包，本轮已删除下载的 installer，但后续测试应临时禁用自动更新。
6. 直接 Playwright runtime 缺依赖，需补齐或只走 web-search Bridge。

## 13. 下一步建议

建议进入 Phase 1A-DeepSeekSkillMiniLoop，而不是 WhiteLabelMVP。

最小闭环目标：

1. 临时禁用自动更新，避免测试时下载上游安装包。
2. 将 `domestic_signal_growth` 包成正式 LobsterAI Skill 或 MCP stdio 工具。
3. 将高价值业务任务默认模型切到 `deepseek/deepseek-v4-pro`。
4. 在 Cowork 中手动执行一次职业证书考评推广任务。
5. 生成报告、内容建议、跟进草稿、待办清单，但不真实外发。
6. 再决定是否进入 WhiteLabelMVP。

## 14. 最终结论

结论：B. 能力部分成立，先修复具体阻塞点。

不建议暂停 LobsterAI。LobsterAI + OpenClaw 已经具备继续做“宇智能获客能力”的基础，但还不能宣称业务闭环完全跑通。下一步应优先打通 DeepSeek V4 Pro + domestic_signal_growth + Cowork 的最小端到端任务。

## 15. 本阶段执行命令摘要

- `D:\OpenClaw\v2\scripts\v2-task-precheck.ps1`
- `npm run electron:dev:openclaw`
- `web-search/scripts/search.sh "职业证书培训机构营销方式" 5`
- `web-search/scripts/search.sh "职业证书考评 培训机构 人力资源公司 推广" 5`
- Python docx/xlsx/pdf/pptx 最小文件生成与读取测试
- Playwright 最小公开网页访问测试
- 官方 Kit Store 公开目录读取
- `D:\OpenClaw\v2\skills\domestic_signal_growth\hello_growth.ps1`

安全确认：

- 未读取 `D:\OpenClaw\secrets`。
- 未提交 API Key、Token、Cookie、浏览器 Profile。
- 未真实发送邮件、私信、评论、发帖。
- 未安装专家套件。
- 未安装上游更新包。
- 自动下载到 LobsterAI updates 目录的官方更新 exe 已删除。

