# Phase 1A-UI-E2E：LobsterAI UI 人工发起端到端任务验证

## 1. 测试日期

- 测试时间：2026-07-01 18:01:03 +08:00
- 当前阶段：Phase 1A-UI-E2E
- 阶段目标：通过 LobsterAI 桌面 UI 手动发起 Cowork 任务，验证 DeepSeek V4 Pro + domestic_signal_growth + web-search 是否能形成最小业务闭环。

## 2. 当前 LobsterAI commit

- LobsterAI / client-shell 当前 commit：`c7ad9346e82e55449bf656d42a5365b245cc9d62`
- 宇智能工作区当前基线 commit：`c7ad934`

## 3. OpenClaw gateway 状态

- 启动命令：`npm run electron:dev:openclaw`
- Electron UI：已启动。
- OpenClaw runtime gateway：已启动并监听 `127.0.0.1:18790`。
- CoworkProxy：已启动并监听本地端口。
- web-search bridge：已启动并监听 `127.0.0.1:8923`。
- Gateway 日志显示：`gateway ready`。

## 4. 自动更新是否禁用

- 企业配置中 `disableUpdate=true`。
- 本轮未观察到官方更新包下载或安装。
- Gateway 日志仅提示存在上游 OpenClaw 更新，不执行更新。

## 5. 当前模型是否为 deepseek/deepseek-v4-pro

- Gateway 启动日志显示默认 agent model 为 `deepseek/deepseek-v4-pro`。
- 但是本次 UI 会话创建时，Cowork 前端使用了会话级模型覆盖：`deepseek/deepseek-v4-flash`。
- 结论：底层 Gateway 默认模型已是 V4 Pro，但 UI 当前模型下拉会覆盖默认模型，本次人工 UI 任务实际没有满足“必须使用 V4 Pro”的要求。

## 6. Cowork UI 是否接收任务

- 是。
- 用户在 LobsterAI UI 中发送了任务，Cowork 创建了 session。
- 本次截图中的实际输入是“研究一下现在的健身市场行情”，不是阶段要求中的完整职业证书考评推广任务文本。

## 7. 是否出现权限审批

- Gateway 出现了权限升级请求。
- 请求类型：`scope-upgrade`
- 请求客户端：`gateway-client`
- 请求 scope：`operator.admin`
- 请求记录已写入：`%APPDATA%\LobsterAI\openclaw\state\devices\pending.json`
- UI 聊天区没有出现可点击的权限批准弹窗。

## 8. 用户是否手动批准

- 否。
- 本阶段要求不绕过权限门禁，因此没有直接修改 pending 文件，也没有用 CLI 强行批准。
- 当前阻塞点是：权限请求已生成，但 LobsterAI Cowork 普通 UI 没有暴露可用的设备权限审批入口。

## 9. web-search 是否被触发

- 本次 UI 任务未触发 web-search。
- 原因：Cowork 在 GatewayClient 握手阶段被 `operator.admin` scope upgrade 阻塞，未进入模型执行和工具调用阶段。
- web-search bridge 本身可启动，且前置阶段已验证过搜索桥可用。

## 10. domestic_signal_growth 是否被触发

- 本次 UI 任务未触发 domestic_signal_growth。
- 原因同上：任务在 GatewayClient 握手阶段失败，未进入 Skill 调用阶段。
- domestic_signal_growth Skill 文件已同步到 LobsterAI 用户 Skill 目录，但 Cowork UI 端是否能识别并调用，仍未完成验证。

## 11. 最小业务任务是否完成

- 未完成。
- Cowork UI 能接收任务，但没有生成业务输出。
- 失败信息：`OpenClaw gateway client connect timeout after 60000ms.`
- 根因不是 Gateway 未启动，而是 GatewayClient 请求 `operator.admin` 后等待审批，审批未完成导致握手失败。

## 12. 输出摘要

本轮 UI E2E 的有效证据：

- Electron UI 能启动。
- OpenClaw runtime 能启动。
- Gateway 能进入 ready 状态。
- Gateway 默认模型能配置为 `deepseek/deepseek-v4-pro`。
- Cowork UI 能接收用户输入并创建 session。
- 安全门禁有效：当 Cowork backend 请求更高权限时，Gateway 阻止连接并生成 pending approval。

本轮未达成：

- UI 会话实际使用了 `deepseek/deepseek-v4-flash`，不是 V4 Pro。
- 普通 Cowork UI 没有展示可操作的 `operator.admin` 权限批准入口。
- web-search 未触发。
- domestic_signal_growth 未触发。
- 职业证书考评推广的完整业务闭环未跑通。

## 13. 失败点

### 阻塞点 1：权限审批入口缺失

Cowork 的 GatewayClient 在 `openclawRuntimeAdapter.ts` 中请求 `operator.admin` scope。Gateway 正确创建 pending approval，但普通用户界面没有显示可批准入口，最终导致连接超时。

分类：B. UI 端到端部分成立，先做最小 Skill/MCP 修复。

### 阻塞点 2：UI 模型覆盖 Gateway 默认模型

虽然 Gateway 默认模型为 `deepseek/deepseek-v4-pro`，但本次 UI 会话根据下拉框覆盖为 `deepseek/deepseek-v4-flash`。如果后续继续要求深度分析必须使用 V4 Pro，需要修正 UI 默认模型或任务级模型选择策略。

### 阻塞点 3：Skill 调用仍未被 UI 证明

domestic_signal_growth 已安装到用户 Skill 目录，但由于权限握手失败，无法判断 Cowork 是否能在 UI 任务中自动发现和调用该 Skill。

## 14. 安全检查结果

- 没有绕过 operator.write / operator.admin 权限门禁。
- 没有修改 OpenClaw 安全策略。
- 没有自动点击同意、登录或授权。
- 没有读取 secrets 内容。
- 没有提交 API Key、Token、Cookie 或浏览器 Profile。
- 没有连接真实社媒账号。
- 没有真实发送邮件、私信、评论或发帖。
- 没有自动安装官方专家套件。
- 没有下载官方更新包。
- 注意：日志中有账号、token、key 的脱敏或非脱敏运行时信息，报告不收录敏感原文。

## 15. 是否允许进入 Phase 2

结论：B. UI 端到端部分成立，先做最小 Skill/MCP 修复。

不建议直接进入 Phase 2 的完整 domestic_signal_growth 业务开发。建议先做一个小的修复阶段：

1. 给 Cowork 的 Gateway scope upgrade 增加明确的用户可见审批入口，或改为最小可用 scope。
2. 确保普通 UI 默认深度分析模型为 `deepseek/deepseek-v4-pro`，避免任务被会话下拉覆盖到 Flash。
3. 在 UI 中增加“本地 Skill 可用性检查”，确认 domestic_signal_growth 能被 Cowork 发现。
4. 修复后重新执行同一条职业证书考评推广任务。

## 16. 回滚方式

- 本阶段未修改 LobsterAI 源码。
- 本阶段未修改 OpenClaw 配置。
- 本阶段只新增本报告文件。
- 如需回滚，仅删除本报告或回退对应 Git commit。

