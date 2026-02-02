---
title: "SS004 - Git commit 阶段阻断（Git hook）"
id: "SS004"
target_version: "v0.1"
status: "已批准"
owner: "AI 助手"
story_points: "TBD"
jira_id: ""
created_date: "2026-01-29"
last_updated: "2026-02-02"
related_prd_feature: "../index.md"
---

## 1. 用户故事描述 (User Story Description)
**作为一个** 开发者/仓库管理员  
**我想要** 在 `git commit` 时自动运行敏感信息扫描，并在“严重命中”时阻断提交  
**以便于** 把明显的高风险泄露拦截在本地提交阶段

## 2. 验收标准 (Acceptance Criteria - AC)
- [ ] AC1: 提供一种“安装/启用 hook”的方式（例如 `python -m themis install-hooks` 或脚本），将 hook 安装到 `.git/hooks/`
- [ ] AC1.1: 一键接入：在无额外手工配置的情况下，单条命令即可完成接入（安装 hook + 使用默认规则/默认配置）
- [ ] AC1.2: 幂等安装：重复执行安装命令不会重复注入 hook（同一仓库多次执行结果一致）
- [ ] AC1.3: 已有 `pre-commit` 时自动合并：保留原 hook 文件为 `.git/hooks/pre-commit.themis.bak`，新 hook 先执行 themis，再执行原 hook；themis 失败时不再执行原 hook，直接阻断；原 hook 失败时透传原退出码
- [ ] AC1.4: 支持卸载 hook（`uninstall-hooks`）：可恢复到安装前状态（存在备份则恢复备份，不存在备份则删除 themis 注入 hook）
- [ ] AC2: Hook 固定在 `pre-commit` 阶段触发，执行 `git diff --cached -U0 --no-color` 生成临时 diff 文件，并调用 `themis scan --platform <platform> --diff-file <tempfile>`
- [ ] AC2.1: 非 git 仓库、无法读取 staged diff、或 diff 为空时：打印可读提示并按“安全失败”策略返回非 0（阻断提交）；默认不可配置为放行
- [ ] AC3: 当命中达到阻断阈值（默认 `severity >= critical`）时，阻断提交并给出可操作的提示（包含规则、文件、行号、脱敏预览）
- [ ] AC3.1: 阈值可配置（键名 `scan.block_on_severity`），优先级为：命令行参数 > 配置文件 > 默认值（`critical`）
- [ ] AC4: 支持豁免机制（路径/注释/baseline）在 hook 场景同样生效
- [ ] AC5: Hook 不修改用户代码，不产生网络依赖（除非明确启用）
- [ ] AC6: Hook 性能要求：只处理 staged diff 的新增/修改行；跳过二进制与超大文件
- [ ] AC6.1: 性能量化验收：在 200 行以内 staged diff、默认规则下，本地执行 `pre-commit` 扫描耗时 `p95 <= 1s`，`p99 <= 2s`；基线环境为 4 核 CPU / 8GB RAM / Python 3.10+，每项场景至少采样 30 次

## 3. 背景与上下文 (Context & Background)
- 你要求“commit 有严重问题要阻断提交”，因此需要在本地 git hooks 或等价机制中执行扫描。
- hook 本身不具备强制性（可被关闭/绕过），但能显著降低误提交概率；强制性通常来自服务端（本项目暂不覆盖）。

## 4. 技术设计与实现计划 (Technical Design & Implementation Plan)

### 4.1. 提议的解决方案/方法 (Proposed Solution / Approach)
- 使用 `pre-commit` hook（不是 pre-commit 框架）实现（固定在 `pre-commit` 阶段触发）：
  - 读取 staged diff（`git diff --cached -U0 --no-color`），将其交给扫描器的 `diff` 模式（仅扫描新增/修改行）
  - 根据配置的 `block_on_severity` 计算退出码，非 0 则阻断提交（默认仅 `critical`）
- 提供 `install-hooks` 命令：
  - 写入一个轻量脚本到 `.git/hooks/pre-commit`
  - 保留用户现有 hook：若已有 `pre-commit`，需自动合并执行顺序，确保不与现有 hook 冲突
  - 无配置文件时使用内置默认规则；如存在 `.themis.<platform>.yml` 则按 `--platform` 自动加载（`.themis.android.yml/.themis.ios.yml/.themis.backend.yml/.themis.web.yml`）
  - 安装命令支持显式指定平台（例如 `themis install-hooks --platform android`）

性能默认策略（用于保证 commit 快）：
- 不做全仓库文件遍历
- 只扫描 diff 中的新增/修改行（不扫描上下文行）
- 规则执行顺序优先“高置信度低成本”（例如固定前缀/结构特征），再运行成本更高的熵检测类规则（可配置开关）

### 4.2. 潜在风险与缓解 (Potential Risks & Mitigation)
- Hook 冲突：用户已有 pre-commit hook，需要明确“覆盖/合并/失败退出”策略
- 误报导致阻断：依赖规则质量与豁免机制；建议支持 `--no-verify` 绕过但记录提示

## 5. 任务 (TDD 聚焦) (Tasks (TDD Focused))
- [x] 1. **测试**：`install-hooks` 首次安装与幂等安装（重复安装不重复注入）
- [x] 2. **测试**：已有 `pre-commit` 时的自动合并策略（备份命名、执行顺序、失败传播）
- [x] 3. **测试**：`git diff --cached -U0 --no-color` 生成 diff-file 并传给 `themis scan --diff-file`
- [x] 4. **测试**：非 git 仓库 / staged diff 获取失败 / 空 diff 的安全失败路径
- [x] 5. **测试**：阻断阈值默认值（`critical`）与配置覆盖优先级（CLI > 配置 > 默认）
- [x] 6. **测试**：hook 场景下路径/注释/baseline 豁免生效
- [x] 7. **实现**：`install-hooks` 与 `uninstall-hooks`（可回滚到原 hook）
- [x] 8. **实现**：`pre-commit` 执行器（staged diff 采集、临时文件管理、调用 scan）
- [ ] 9. **实现**：阻断阈值联动与错误码映射（保持与 CLI 一致）
- [ ] 10. **重构**：抽离 hook 安装/执行公共逻辑，避免 CLI 与脚本重复实现
- [ ] 11. **测试**：端到端（临时 git repo：critical 阻断、非 critical 放行、豁免放行）
- [ ] 12. **测试**：性能基线（200 行 staged diff，统计 `p95/p99`）
- [ ] 13. **测试**：副作用校验（hook 执行前后工作区文件哈希一致，确保不修改用户代码）
- [ ] 14. **测试**：离线校验（禁网环境执行 hook，扫描流程不依赖外网可正常完成）

## 6. 约束与依赖关系 (Constraints & Dependencies)
- 约束：hook 必须轻量，不显著拖慢 commit；不引入网络依赖
- 依赖：依赖 SS001 CLI 与 SS002 diff 解析能力

## 7. 图表 (可选) (Diagrams (Optional))
（无）

## 8. 开发笔记与日志 (Development Notes & Log)
- 2026-01-29 - AI: Story 草稿，待确认 hook 覆盖策略与阻断阈值配置项命名。
- 2026-02-02 - AI: 根据评审补全 AC 与任务细节：明确 hook 合并/回滚策略、diff-file 传递方式、阈值配置优先级、异常路径与性能量化指标。
- 2026-02-02 - AI: 进一步收敛验收口径：补充 hook 失败短路与退出码透传、空 diff 默认阻断不可配置放行、性能基线环境与采样次数。
- 2026-02-02 - AI: 补充 AC1.4，与任务中的 `uninstall-hooks` 对齐，避免“有任务无验收”歧义。
- 2026-02-02 - AI: 补充测试任务 13/14，覆盖“无代码副作用”和“离线可运行”两个 AC5 关键验证点。
- 2026-02-02 - AI: 完成任务 5.1，新增 `tests/test_hook_install.py` 覆盖首次安装、幂等安装、已有 hook 合并备份；当前为 TDD 红阶段（`themis.hooks` 尚未实现）。
- 2026-02-02 - AI: 完成任务 5.2，补充 `tests/test_hook_install.py` 的合并细节用例（themis 先执行、失败短路阻断），当前仍为 TDD 红阶段（`themis.hooks` 未实现）。
- 2026-02-02 - AI: 完成任务 5.3，补充 `tests/test_hook_install.py` 的 diff 采集与 `--diff-file` 传参用例（`git diff --cached -U0 --no-color` + scan 命令断言）；当前仍为 TDD 红阶段（`themis.hooks` 未实现）。
- 2026-02-02 - AI: 完成任务 5.4，新增 `tests/test_hook_runner.py` 覆盖非 git 仓库、staged diff 获取失败、空 diff、scan 失败四类安全失败路径；当前仍为 TDD 红阶段（`themis.hooks` 未实现）。
- 2026-02-02 - AI: 完成任务 5.5，新增 `tests/test_hook_threshold.py` 覆盖阻断阈值默认值（`critical`）、配置覆盖与 CLI 覆盖优先级，以及非法阈值校验；当前仍为 TDD 红阶段（`themis.hooks` 未实现）。
- 2026-02-02 - AI: 完成任务 5.6，新增 `tests/test_hook_exemptions.py` 覆盖 hook 场景下路径与 baseline 豁免放行；当前仍为 TDD 红阶段（`themis.hooks` 未实现）。
- 2026-02-02 - AI: 完成任务 5.7，实现 `themis/hooks.py` 中 `install_hooks` / `uninstall_hooks`（含已有 hook 合并备份与回滚恢复），`tests/test_hook_install.py` 通过（7/7）。
- 2026-02-02 - AI: 完成任务 5.8，在 `themis/hooks.py` 实现 `run_pre_commit_hook` 与 `run_command`（staged diff 采集、临时 diff 文件、调用 `themis scan --diff-file`、失败分支错误输出）；`tests/test_hook_runner.py` 与 `tests/test_hook_install.py` 共 11 个用例通过。

## 9. AI 交互日志 (Chat Command Log - AI Interaction Record)
- 用户: 工具只需要支持 commit 与 merge request 两个节点；commit 严重命中要阻断提交（默认仅 critical）；MR 使用 GitLab CI 回写 discussion；多仓多平台各自配置文件。
- 用户: 同意细化 SS004 文档，要求从开发者视角降低实现歧义。
- 用户: 同意继续补充 AC 细节，进一步降低实现与验收歧义。
- 用户: 同意补充 AC1.4（卸载 hook 验收项）与任务对齐。
- 用户: 要求补充测试任务，增强 AC 通过保障。
- 用户: 执行 SS004 任务 5.1。
- 用户: 执行 SS004 任务 5.2。
- 用户: 执行 SS004 任务 5.3。
- 用户: 执行 SS004 任务 5.4。
- 用户: 执行 SS004 任务 5.5。
- 用户: 执行 SS004 任务 5.6。
- 用户: 执行 SS004 任务 5.7。
- 用户: 执行 SS004 任务 5.8。
