# Phase PACK-1：宇智能可移植安装包 PoC 报告

## 1. 测试日期

2026-07-03

## 2. 本阶段目标

验证宇智能主线能力是否可以被整理成一个可复制、可验证、可迁移的本地包 PoC。当前阶段不做正式 exe 安装包，不做白标发布，不打包真实项目数据。

## 3. GitHub 推送

- 远程仓库：`https://github.com/zemumu133/yuzhineng`
- 推送分支：`merge-growth-os-cleanroom`
- 已推送 commit：`3fa461c85d317c29c5c5245fe85cf40e45728ea7`
- Pull request 地址提示：`https://github.com/zemumu133/yuzhineng/pull/new/merge-growth-os-cleanroom`
- 未创建正式 release/tag。

## 4. 新增或修改文件

- `.gitignore`
- `v2/packaging/PACK1_PORTABLE_POC_CN.md`
- `v2/scripts/create-pack1-portable-poc.py`
- `v2/scripts/create-pack1-portable-poc.ps1`
- `v2/tests/test_pack1_portable_poc.py`
- `v2/GITHUB_RELEASE_PREP_CN.md`
- `v2/reports/PHASE_PACK1_PORTABLE_POC_REPORT_CN.md`

## 5. 生成包路径

```text
D:\OpenClaw\v2\packages\yuzhineng-pack1-portable-poc
```

该目录为本地生成产物，已通过 `.gitignore` 排除，不提交 Git。

## 6. 包内主要内容

- `openclaw-v2\v2\config\agent_taxonomy.json`
- `openclaw-v2\v2\growth_os`
- `openclaw-v2\v2\skills\domestic_signal_growth`
- `openclaw-v2\v2\skills\product_intelligence`
- `openclaw-v2\v2\workflows`
- `openclaw-v2\v2\scripts`
- `tools\restore-agent-taxonomy.ps1`
- `tools\start-yuzhineng-portable.ps1`
- `tools\open-projects-index.ps1`
- `tools\verify-pack1.ps1`
- `README_安装_CN.md`
- `PACKAGE_MANIFEST.json`

## 7. 明确排除内容

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

## 8. PACK-1 验收点

1. 新设备恢复 Agent taxonomy：已提供 `tools\restore-agent-taxonomy.ps1`，内部调用标准 Agent 修复脚本。
2. 新设备启动 LobsterAI 后默认进入宇智能总控 Agent：已通过 taxonomy 中 `is_default` 和恢复脚本固化，仍依赖目标电脑已准备 LobsterAI/OpenClaw runtime。
3. `projects_index.html` 或成果中心可被普通用户找到：已提供 `tools\open-projects-index.ps1`；没有成果时会提示先运行任务。
4. 打包版不提交运行数据：包生成器和 `.gitignore` 均排除运行数据、项目成果、数据库、日志、密钥和构建产物。

## 9. 运行命令

```powershell
git push -u github-yuzhineng merge-growth-os-cleanroom
python -m unittest D:\OpenClaw\v2\tests\test_pack1_portable_poc.py -v
python -m unittest discover D:\OpenClaw\v2\tests -v
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\OpenClaw\v2\scripts\create-pack1-portable-poc.ps1 -Force
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\OpenClaw\v2\packages\yuzhineng-pack1-portable-poc\tools\verify-pack1.ps1
```

## 10. 测试结果

- PACK-1 单测：2 项通过。
- v2 全量测试：15 项通过。
- 包生成：通过，复制 127 个文件。
- 包安全扫描：通过，违规路径 0 个。
- 包内自检：通过。

## 11. 安全结论

- 未读取 secrets。
- 未提交密钥。
- 未提交数据库。
- 未提交日志。
- 未提交运行数据或项目成果。
- 未提交 LobsterAI 上游源码或 node_modules。
- 未真实发布、评论、私信或发邮件。
- 外部动作策略继续保持 `draft_only` 或 `approval_required`。

## 12. 已知限制

1. 当前是可移植包 PoC，不是正式 Windows 安装包。
2. LobsterAI/OpenClaw runtime 仍需在目标电脑按 PoC 路径准备。
3. 当前未做干净机完整恢复测试。
4. 当前未隐藏 LobsterAI 上游品牌，也未做签名、自动更新和正式安装卸载。
5. PowerShell 控制台在部分命令输出中会出现中文编码显示问题，但生成文件为 UTF-8。

## 13. 回滚方式

1. 删除本地生成目录：`D:\OpenClaw\v2\packages\yuzhineng-pack1-portable-poc`。
2. 回退本阶段 Git commit。
3. 如果已在 GitHub 使用该分支，可删除远程分支或用后续修复 commit 覆盖。

## 14. 结论

结论：B+。PACK-1 可移植包 PoC 已能生成并通过本机自检，但尚未完成干净机恢复验证，因此还不能作为正式安装包发布。

建议下一步执行 PACK-1.1：干净机恢复验证，重点测试目标电脑上 Agent taxonomy 恢复、LobsterAI 启动、宇智能总控 Agent 默认入口、项目成果入口和无运行数据泄漏。
