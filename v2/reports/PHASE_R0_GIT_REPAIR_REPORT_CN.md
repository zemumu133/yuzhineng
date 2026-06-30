# Phase R0-FixGit：Git 环境修复与仓库基线建立报告

## 1. 测试日期

2026-06-30

## 2. 是否找到系统 Git

未找到。系统 PATH 中没有 `git`，以下常见路径也未发现 Git：

- `C:\Program Files\Git\cmd\git.exe`
- `C:\Program Files\Git\bin\git.exe`
- `D:\DevTools\Git\cmd\git.exe`
- `D:\DevTools\Git\bin\git.exe`

## 3. 是否使用便携 Git

是。已使用 Git for Windows 官方 release 的 MinGit 便携包。

下载来源：

`https://github.com/git-for-windows/git/releases/download/v2.54.0.windows.1/MinGit-2.54.0-64-bit.zip`

下载文件：

`D:\DevTools\downloads\MinGit-2.54.0-64-bit.zip`

下载包 SHA256：

`04F937E1F0918B17B9BE6F2294CB2BB66E96E1D9832D1C298E2DE088A1D0E668`

## 4. Git 路径

`D:\DevTools\Git\cmd\git.exe`

## 5. Git 版本

`git version 2.54.0.windows.1`

## 6. 是否初始化 D:\OpenClaw 仓库

是。`D:\OpenClaw\.git` 已初始化。

## 7. .gitignore 创建/更新情况

已创建 `D:\OpenClaw\.gitignore`。

主要忽略范围：

- `secrets/`
- `logs/`
- `backups/`
- `data/`
- `exports/`
- `database/`
- `browser_profiles/`
- `node_modules/`
- `dist/`
- `build/`
- `.cache/`
- 浏览器 Cookie / Network / Local Storage / Session Storage
- `*.env`
- `*.key`
- `*.token`
- `*.pem`
- `*.p12`
- `*.pfx`
- `*.sqlite`
- `*.log`
- `*.zip`
- 旧 Phase 1.x 控制台实现目录

## 8. 提交文件清单

本次只计划提交：

- `.gitignore`
- `v2/README_V2_CN.md`
- `v2/V2_PRODUCT_DIRECTION_CN.md`
- `v2/V2_ARCHITECTURE_CN.md`
- `v2/V2_PHASE_PLAN_CN.md`
- `v2/V2_COMPONENT_DECISION_LOG_CN.md`
- `v2/scripts/v2-preflight-check.ps1`
- `v2/reports/*.md`

## 9. 被排除文件说明

以下内容被排除，不进入 Git 基线：

- 真实密钥目录
- 日志目录
- 数据库目录
- 备份压缩包
- 浏览器 Profile
- 旧控制台运行目录
- 旧脚本和旧业务实现目录
- 依赖、缓存和构建产物

## 10. 是否发现密钥风险

提交候选文件中未发现密钥类文件、数据库、日志、备份、浏览器 Profile、依赖包或构建产物。

未读取 `secrets` 内容。

## 11. commit hash

本报告随 Git 基线提交一起纳入版本库。最终 commit hash 由提交完成后生成，见任务最终输出。

## 12. tag 名称

计划创建：`legacy-console-phase-1-9A`

如果名称冲突，则使用日期后缀。

## 13. 当前分支

提交完成后将切换到：`v2-open-source-growth-system`

如果名称冲突，则使用日期后缀。

## 14. 是否允许继续执行 R0.5

提交、tag、v2 分支和最终安全检查全部通过后，允许继续执行 R0.5。

## 15. 下一步建议

执行 Phase R0.5：Codex 最高原则、工作流、子 Agent 与阶段门禁固化。

