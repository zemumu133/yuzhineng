# PACK-1：宇智能可移植安装包 PoC

## 目标

PACK-1 不做正式商业安装包，也不打包真实用户数据。当前目标是验证“换一台 Windows 电脑后，能否用同一套仓库文件和脚本恢复宇智能主线能力”。

本阶段可移植包应覆盖：

1. 标准宇智能 Agent taxonomy。
2. Growth OS 主线能力代码。
3. domestic_signal_growth 与 product_intelligence Skill。
4. 制造业获客多 Agent 工作流。
5. Agent 恢复脚本和启动脚本。
6. 项目成果入口说明。
7. 安全边界说明。

## 不包含内容

可移植包不得包含：

- `secrets/`
- `.env`、API Key、Token、Cookie、浏览器 Profile
- `logs/`
- `database/`
- `backups/`
- `data/`
- `exports/`
- `v2/projects/` 真实项目成果
- `v2/data/` UI 运行轨迹
- `v2/runtimes/`
- `v2/client-shell/lobsterai/src/` 上游源码
- `node_modules/`
- `dist/`、`build/`、缓存和构建产物

## 使用方式

在开发机运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\OpenClaw\v2\scripts\create-pack1-portable-poc.ps1
```

默认输出目录：

```text
D:\OpenClaw\v2\packages\yuzhineng-pack1-portable-poc
```

该目录为本机生成产物，默认不提交 Git。

## 新设备恢复路径

1. 将 `yuzhineng-pack1-portable-poc` 复制到新电脑。
2. 按包内 `README_安装_CN.md` 准备 LobsterAI/OpenClaw runtime。
3. 运行 `tools\restore-agent-taxonomy.ps1` 恢复 9 个标准宇智能 Agent。
4. 运行 `tools\start-yuzhineng-portable.ps1` 启动桌面端。
5. 完成任务后用 `tools\open-projects-index.ps1` 打开项目成果入口。

## 当前限制

1. 这不是正式 exe 安装包。
2. LobsterAI 上游源码和 runtime 仍需按现有 PoC 路径准备。
3. 不包含真实项目成果，只验证归档入口和恢复脚本。
4. 不做自动发布、自动评论、自动私信、自动邮件。
5. 打包版隐藏 DevTools、签名、自动更新和白标化仍属于后续阶段。
