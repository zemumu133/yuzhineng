# Phase 1A-DevAutoRunGate：UI 真实鼠标验证与 Gateway 修复报告

测试日期：2026-07-02

## 1. 本轮目标

修复用户在 LobsterAI 桌面端随机选择 Agent 后出现的不可用问题，并使用真实 UI 鼠标路径验证：

- 不通过 CLI 代发 Cowork。
- 不绕过 OpenClaw 权限门禁。
- 不申请全局 `operator.admin`。
- 普通 Agent 对话使用 `deepseek/deepseek-v4-pro`。
- 不真实发送邮件、私信、评论、发帖。

## 2. 根因

发现两个主要问题：

1. GatewayClient 未显式声明 scope 时会落到 `operator.admin` + device pairing 默认路径，桌面端无法稳定展示该配对/提权流程，导致 UI 中出现 `OpenClaw gateway client connect timeout after 60000ms`。
2. 部分 Agent 保留了旧模型选择，UI 会显示或实际使用 DeepSeek V4 Flash，导致“主模型是 V4 Pro”的体验不一致。

## 3. 修改文件

已实际修改但位于被主仓库忽略的 LobsterAI 上游源码目录：

- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\main\libs\agentEngine\openclawRuntimeAdapter.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\store\slices\modelSlice.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\config.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\shared\providers\constants.ts`
- `D:\OpenClaw\v2\client-shell\lobsterai\src\src\renderer\services\config.ts`

主仓库已跟踪文件：

- `D:\OpenClaw\v2\scripts\start-yuzhineng.ps1`
- `D:\OpenClaw\v2\patches\lobsterai-dev-autorun-gateway-scope-and-v4-pro.patch`
- `D:\OpenClaw\v2\reports\LOBSTERAI_DEV_AUTORUN_GATE_REPORT_CN.md`

## 4. 修复内容

Gateway 修复：

- 显式使用 `operator.write`。
- 显式设置 `deviceIdentity: null`。
- 阻止 GatewayClient 走隐式 `operator.admin` 配对路径。
- `sessions.patch` 因缺少 `operator.admin` 失败时不再阻塞 `chat.send`。

模型修复：

- DeepSeek 默认模型改为 `deepseek-v4-pro`。
- Provider 列表优先显示 V4 Pro。
- 对普通 Agent/Cowork 路径中的旧模型做兜底迁移：
  - `deepseek-chat`
  - `deepseek-reasoner`
  - `deepseek-v4-flash`

启动修复：

- “宇智能”桌面快捷方式仍指向 `D:\OpenClaw\v2\scripts\start-yuzhineng.ps1`。
- 启动脚本已改为 `npm run electron:dev:openclaw`。
- 启动时临时加入 PortableGit、Git、runtime shims 和 `OPENCLAW_SRC`，不修改系统 PATH。

## 5. 验证结果

命令验证：

- `npm run compile:electron`：通过。
- `npx tsc --noEmit`：通过。
- `npm run electron:dev:openclaw`：启动到 Electron UI，Gateway ready。

真实鼠标 UI 验证：

- 使用 Windows 原生鼠标/键盘自动化点击 LobsterAI 窗口。
- 选择非主 Agent：`宇智能获客 Agent`。
- 点击输入框，粘贴测试任务。
- 用鼠标点击发送按钮。
- UI 进入执行中状态。
- UI 最终返回：`宇智能获客 Agent 可以正常工作`。

截图证据：

- `D:\OpenClaw\v2\reports\assets\lobsterai\ui-real-random-agent-ready-to-click-send.png`
- `D:\OpenClaw\v2\reports\assets\lobsterai\ui-real-random-agent-click-send.png`
- `D:\OpenClaw\v2\reports\assets\lobsterai\ui-real-random-agent-after-click-send-90s.png`

日志证据摘要（已脱敏）：

- UI 创建 session 使用：`deepseek/deepseek-v4-pro`
- GatewayClient handshake succeeded
- `chat.send` acknowledged
- Agent run provider：`deepseek`
- Agent run model：`deepseek-v4-pro`
- Provider fetch status：`200`
- 最终消息 metadata model：`deepseek-v4-pro`

## 6. 已知限制

1. `sessions.patch` 仍需要 `operator.admin`，当前策略是非 admin 客户端跳过该同步步骤，让 Gateway 使用已配置的 V4 Pro 模型。这是刻意保守处理，不申请全局 admin。
2. 可选插件 `moltbot-popo` 仍可能因上游网络 `ECONNRESET` 被跳过，不影响本轮 Cowork/Agent 基础对话。
3. 开发模式仍提示 bundled Python runtime 缺失，后续打包阶段需要单独处理。
4. 截图文件仅作为本机验证证据，当前未加入 Git。
5. LobsterAI 上游源码目录被主仓库忽略，真实源码改动已用 patch note 记录，后续进入正式 fork 或补丁管理时需要固化。

## 7. 安全检查

- 未读取或提交 secrets 文件。
- 未提交 API Key、Token、Cookie、浏览器 Profile。
- 未提交数据库、日志、缓存、node_modules、构建产物。
- 未执行真实外部发送。
- 未连接真实社媒账号。
- 未绕过验证码、登录墙或平台限制。

## 8. 结论

结论：B+，UI 端到端基础 Agent 对话已经恢复，且真实鼠标路径验证通过。

当前可以继续使用 LobsterAI + OpenClaw + DeepSeek V4 Pro 做下一步业务能力验证。下一阶段建议把 `domestic_signal_growth` 做成正式可被 Cowork 稳定识别的 Skill/MCP 工具，并继续用真实 UI 鼠标路径测试“职业证书考评服务推广”这类完整任务。
