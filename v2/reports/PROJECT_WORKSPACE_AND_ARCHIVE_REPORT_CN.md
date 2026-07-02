# Phase 2C：制造业获客成果归档、项目工作区与结果查看入口

## 1. 测试日期

2026-07-02

## 2. 阶段目标

本阶段目标是把 Phase 2B 生成的制造业获客成果从“散落的运行输出”整理为可交付、可查看、可迁移的项目工作区。

每个项目工作区包含：

- input.json
- project_manifest.json
- sources.json
- skill_output.json
- report.md
- handoff.docx
- todos.json
- safety_check.json
- README_CN.md

同时生成全局入口：

- D:\OpenClaw\v2\projects\projects_index.json
- D:\OpenClaw\v2\projects\index.html

## 3. 修改文件清单

新增：

- D:\OpenClaw\v2\scripts\archive_manufacturing_growth_result.py
- D:\OpenClaw\v2\scripts\archive_manufacturing_growth_result.ps1
- D:\OpenClaw\v2\tests\test_archive_manufacturing_growth_result.py
- D:\OpenClaw\v2\reports\PROJECT_WORKSPACE_AND_ARCHIVE_REPORT_CN.md

修改：

- D:\OpenClaw\.gitignore

本地生成但不提交 Git：

- D:\OpenClaw\v2\projects\
- D:\OpenClaw\v2\data\ui-runs\
- D:\OpenClaw\v2\reports\assets\phase2c-project-workspace-ui\

## 4. 新增脚本

### archive_manufacturing_growth_result.py

用途：

- 读取 Phase 2B 任务输出目录。
- 生成独立项目归档目录。
- 复制或生成 report.md。
- 复制或生成 handoff.docx。
- 写入 project_manifest.json、todos.json、sources.json、safety_check.json。
- 更新 projects_index.json。
- 生成本地 index.html。

主要参数：

- --task-output-dir
- --projects-root
- --project-slug
- --project-name
- --created-at
- --report-source
- --handoff-source

### archive_manufacturing_growth_result.ps1

用途：

- Windows 用户友好的 PowerShell 包装脚本。
- 调用 Python 归档器。
- 不读取 secrets，不真实发送任何外部动作。

## 5. 项目工作区生成结果

已生成 5 个本地项目归档：

- D:\OpenClaw\v2\projects\20260702-174922-dongguan-electronics-parts
- D:\OpenClaw\v2\projects\20260702-174922-dongguan-fitness-equipment
- D:\OpenClaw\v2\projects\20260702-174922-dongguan-heavy-packaging
- D:\OpenClaw\v2\projects\20260702-175902-phase2c-ui-dongguan-electronics-parts
- D:\OpenClaw\v2\projects\20260702-175902-phase2c-ui-dongguan-heavy-packaging

其中前 3 个来自 Phase 2B 自动任务输出；后 2 个使用 LobsterAI UI 真实生成的 report.md / handoff.docx 作为归档源。

## 6. 索引入口

已生成：

- D:\OpenClaw\v2\projects\projects_index.json
- D:\OpenClaw\v2\projects\index.html

index.html 展示：

- 生成时间
- 产品
- 工厂类型
- 模式
- 来源数量
- 待办数量
- 打开推广方案
- 打开交接单
- 打开待办

所有项目均为 draft_only。发布、评论、私信、邮件必须由用户人工确认和执行。

## 7. UI 鼠标验证结果

本阶段没有可用的真实 Computer Use 插件。实际采用 Windows 本机窗口/鼠标自动化、LobsterAI 桌面 UI 和截图留痕完成验证。

已验证的 UI 任务：

1. 东莞电子配件厂获客任务
   - 产品：电子连接件、线束、充电配件
   - 目标客户：电子厂、品牌商、跨境卖家、维修渠道
   - 结果：LobsterAI UI 生成推广方案 md 和交接单 docx
   - 归档目录：D:\OpenClaw\v2\projects\20260702-175902-phase2c-ui-dongguan-electronics-parts

2. 东莞重型包装纸箱厂获客任务
   - 产品：重型包装纸箱、物流包装、出口包装
   - 目标客户：电商仓储、制造工厂、物流公司、外贸企业
   - 结果：LobsterAI UI 生成推广方案 md 和交接单 docx
   - 归档目录：D:\OpenClaw\v2\projects\20260702-175902-phase2c-ui-dongguan-heavy-packaging

截图证据：

- D:\OpenClaw\v2\reports\assets\phase2c-project-workspace-ui\phase2c-task2-packaging-ready.png
- D:\OpenClaw\v2\reports\assets\phase2c-project-workspace-ui\phase2c-task2-packaging-sent.png
- D:\OpenClaw\v2\reports\assets\phase2c-project-workspace-ui\phase2c-task2-packaging-after-150s.png
- D:\OpenClaw\v2\reports\assets\phase2c-project-workspace-ui\phase2c-project-index-headless.png
- D:\OpenClaw\v2\reports\assets\phase2c-project-workspace-ui\phase2c-first-report-headless.png

## 8. 链接和文件校验

校验结果：

- projects_index.json 中 5 个项目均可读取。
- report.md、handoff.docx、todos.json 共 15 个链接均指向存在的本地文件。
- 首个 report.md 已通过浏览器本地文件截图打开验证。
- handoff.docx 均为有效 docx/zip 文件。

## 9. 测试结果

已运行：

- python -m py_compile D:\OpenClaw\v2\scripts\archive_manufacturing_growth_result.py
- python -m unittest D:\OpenClaw\v2\tests\test_archive_manufacturing_growth_result.py -v
- python -m unittest discover -s D:\OpenClaw\v2\skills\domestic_signal_growth\tests -v
- python -m unittest discover D:\OpenClaw\v2\tests -v
- YUZHINENG_DEV_AUTO_RUN=1 python D:\OpenClaw\v2\scripts\dev-autorun-gate.py --run-phase2b

结果：

- 归档器单元测试通过。
- domestic_signal_growth 测试通过。
- Phase 2B dev auto-run 通过。
- 项目索引和本地结果文件验证通过。

## 10. 安全检查

本阶段没有：

- 读取 secrets 内容。
- 提交 API Key、Token、Cookie。
- 提交数据库、日志、缓存、浏览器 Profile。
- 真实发送邮件。
- 真实私信。
- 真实评论。
- 真实发帖。
- 登录社媒账号。

.gitignore 已追加：

- /v2/projects/
- /v2/data/ui-runs/

原因：项目归档和 UI 运行轨迹属于本地运行数据，不应进入 Git。

## 11. 已知限制

1. 当前归档入口是本地静态 HTML，不是 LobsterAI 内置页面。
2. 本阶段没有开发正式项目管理 UI。
3. docx 打开验证以文件存在和格式有效为主，未做 Word/WPS 视觉截图批量验证。
4. 本阶段没有真正 Computer Use 插件，只使用本机窗口/鼠标自动化和截图。
5. 项目归档目录当前被 .gitignore 排除，迁移时需要复制 D:\OpenClaw\v2\projects 整个目录。

## 12. 回滚方式

如需回滚 Phase 2C 代码变更：

1. 回退 Git 提交 phase-2c-project-workspace-and-result-archive。
2. 删除或保留 D:\OpenClaw\v2\projects\，该目录不受 Git 管理。
3. 删除 D:\OpenClaw\v2\reports\assets\phase2c-project-workspace-ui\，该目录仅为截图证据。

## 13. 结论

结论：A。Phase 2C 成立。

理由：

- 项目工作区结构已生成。
- 归档脚本可重复运行。
- 本地索引页可查看项目成果。
- 至少两个 UI 发起任务已产生可归档成果。
- 推广方案、交接单、待办、安全检查均可归档。
- 全部外部动作保持 draft_only，没有真实发送或发布。

## 14. 下一阶段建议

建议进入 Phase 2D：

- 把项目索引入口整合进“宇智能”的桌面侧边栏或固定工作区。
- 增加项目列表、项目详情、结果查看和人工审批按钮。
- 保持外部动作 draft_only / approval_required，不加入自动发送能力。
