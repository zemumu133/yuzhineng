# LobsterAI PoC 报告

## 1. 测试日期

2026-06-30

## 2. 测试环境

- Windows
- 工作目录：`D:\OpenClaw\v2\client-shell\lobsterai`
- 源码目录：`D:\OpenClaw\v2\client-shell\lobsterai\src`
- npm cache：`D:\DevTools\node\npm-cache`
- npm prefix：`D:\DevTools\node\npm-global`
- OpenClaw 旧控制台：`http://127.0.0.1:18880/` 可访问

## 3. Git 路径

`D:\DevTools\Git\cmd\git.exe`

## 4. Node / npm / pnpm / Python 版本

- Git：`git version 2.54.0.windows.1`
- Node.js：`v24.15.0`
- npm：`11.12.1`
- pnpm：`11.7.0`
- Python：`Python 3.12.10`

## 5. LobsterAI 仓库 URL

`https://github.com/netease-youdao/LobsterAI`

仓库信息：

- 默认分支：`main`
- License：MIT
- GitHub API 查询时 stars：5393
- 查询时间：2026-06-30

## 6. LobsterAI commit hash

`b2317e65785ec02e982895c98c4c82d36d37d5f0`

由于 `git clone --depth 1` 在本机卡在 `index-pack` 阶段，本次使用官方 main 分支 zip 包获取源码，并通过 GitHub API 记录 commit。

源码 zip：

- 路径：`D:\DevTools\downloads\LobsterAI-main.zip`
- SHA256：`05F57E3E7694268FF6452D606EFCBFD0D161E3953ED80E53C33C39F8B6F2444C`

## 7. 使用的包管理器

官方 README 推荐 npm，本次使用 npm。

## 8. 是否使用镜像源

是。

- 第 1 轮：官方默认 npm registry，卡在 Electron 下载阶段。
- 第 2 轮：仅当前命令使用 `https://registry.npmmirror.com` 和 Electron 镜像，未修改全局配置。

## 9. 依赖安装命令

第 1 轮：

```powershell
npm install
```

结果：卡在 `node install.js`，疑似 Electron 二进制下载阶段。

第 2 轮：

```powershell
$env:npm_config_registry="https://registry.npmmirror.com"
$env:ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/"
$env:ELECTRON_BUILDER_BINARIES_MIRROR="https://npmmirror.com/mirrors/electron-builder-binaries/"
npm install --foreground-scripts --loglevel=info
```

结果：成功。

## 10. 依赖安装耗时

- 第 1 轮：约 14 分钟后停止，未完成。
- 第 2 轮：19.24 秒，成功。
- Electron rebuild：12.55 秒，成功。

## 11. 启动命令

首次官方命令：

```powershell
npm run electron:dev:openclaw
```

桌面 UI 验证命令：

```powershell
npm run electron:dev
```

## 12. 是否启动成功

部分成功。

- Electron 桌面 UI：成功启动。
- Vite dev server：成功，`http://localhost:5175/` 返回 HTTP 200。
- Electron 主窗口：存在，窗口标题为 `LobsterAI`。
- Cowork / OpenClaw runtime：未完整成功。

## 13. 是否看到桌面 UI

是。

截图：

`D:\OpenClaw\v2\reports\assets\lobsterai\lobsterai-service-agreement-modal.png`

界面显示“网易有道 LobsterAI 服务协议”弹窗。未点击“我已阅读并同意”，避免代表用户接受服务协议。

## 14. 是否需要 OpenClaw runtime

需要。

README 明确说明 Cowork mode 依赖 OpenClaw agent engine，首次运行应执行 `npm run electron:dev:openclaw` 构建 runtime。

## 15. OpenClaw runtime 构建结果

部分完成。

成功项：

- 已拉取 OpenClaw `v2026.6.1`
- runtime 源码路径：`D:\OpenClaw\v2\runtimes\lobsterai-openclaw-src`
- 已创建默认路径 junction：`D:\OpenClaw\v2\client-shell\lobsterai\openclaw`
- 已应用 LobsterAI 对 OpenClaw 的 15 个 patch

失败项：

- `run-build-openclaw-runtime` 要求 Git Bash / bash。
- 当前 R0-FixGit 使用的是 MinGit，仅有 `git.exe`，没有 `bash.exe`。
- 官方 `npm run setup:mingit` 在下载 PortableGit 阶段异常退出，退出码 `-1073740791`。

失败分类：

`OpenClaw runtime 构建失败 / Git Bash 运行时缺失`

## 16. DeepSeek 接入可行性

可行。

源码中已内置 DeepSeek provider：

- provider：`deepseek`
- default base URL：`https://api.deepseek.com`
- default API format：OpenAI-compatible
- 默认模型包含：`deepseek-v4-flash`、`deepseek-v4-pro`、`deepseek-reasoner`

本阶段未写入真实 API Key。

配置示例仅可使用占位：

```env
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## 17. Skill / MCP / 本地脚本调用可行性

可行，但本阶段只做占位验证。

已创建并验证：

`D:\OpenClaw\v2\skills\domestic_signal_growth\hello_growth.ps1`

运行结果：

`国内营销信号穿透 Skill 占位：输入产品，输出商机判断、内容建议和待办。 当前输入产品：AI获客系统`

源码中存在：

- Skill 管理入口
- MCP stdio / http / sse 配置类型
- MCP command / args / env 字段
- OpenClaw Skill 检测入口

最小接入路径：

1. 先通过 MCP stdio 或本地 Skill 包装 `hello_growth.ps1`。
2. 后续再把 domestic_signal_growth 做成正式 Skill。
3. 不需要从零写完整插件系统。

## 18. Windows 打包路径

可行但未测试。

官方脚本存在：

```powershell
npm run dist:win
```

打包前置：

- OpenClaw runtime 需要构建成功。
- Windows portable Python runtime 需要准备。
- Git Bash / PortableGit 需要修复。

## 19. 商用可行性

继续但有风险。

优点：

- 桌面 UI 能启动。
- 明确是桌面 Agent 客户端形态。
- 内置 DeepSeek provider。
- 内置 Skill / MCP / OpenClaw 体系。
- Windows 打包路径存在。
- 很适合作为“AI 获客与内容运营客户端”的桌面壳候选。

风险：

- 默认会连接 LobsterAI / 有道生产服务。
- 首屏要求用户确认服务协议。
- Cowork / OpenClaw runtime 本机尚未构建成功。
- 开发模式缺少 bundled Python runtime，部分 Skill service 可能不完整。
- 默认产品语义是通用办公助手，需要后续用模板、Skill、入口和默认项目改造成获客客户端。

## 20. 最小改造点

1. 修复 Git Bash / PortableGit runtime 准备。
2. 完成 OpenClaw runtime 构建。
3. 预置 DeepSeek V4 Pro 配置入口，但不写真实 key。
4. 以 MCP stdio 或 Skill 方式接入 `domestic_signal_growth`。
5. 预置“AI 获客 / 内容运营 / 待办审批”模板。
6. 保持高敏感能力默认关闭。

## 21. 结论

继续但有风险。

LobsterAI 可以作为 v2 桌面客户端壳继续验证，但进入深度集成前必须先解决 Git Bash / OpenClaw runtime 构建问题。

## 22. 下一步建议

建议执行 Phase 1A-RepairRuntime：

1. 使用官方 PortableGit 包或本地 archive 修复 `resources\mingit\bash.exe`。
2. 重新执行 `npm run electron:dev:openclaw`。
3. 验证 Cowork / OpenClaw gateway 是否能启动。
4. 再验证 domestic_signal_growth 通过 MCP/Skill 接入。

