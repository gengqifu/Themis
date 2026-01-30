---
title: "SS004 - Git commit 阶段阻断（Git hook）"
id: "SS004"
target_version: "v0.1"
status: "已批准"
owner: "AI 助手"
story_points: "TBD"
jira_id: ""
created_date: "2026-01-29"
last_updated: "2026-01-29"
related_prd_feature: "../index.md"
---

## 1. 用户故事描述 (User Story Description)
**作为一个** 开发者/仓库管理员  
**我想要** 在 `git commit` 时自动运行敏感信息扫描，并在“严重命中”时阻断提交  
**以便于** 把明显的高风险泄露拦截在本地提交阶段

## 2. 验收标准 (Acceptance Criteria - AC)
- [ ] AC1: 提供一种“安装/启用 hook”的方式（例如 `python -m themis install-hooks` 或脚本），将 hook 安装到 `.git/hooks/`
- [ ] AC1.1: 一键接入：在无额外手工配置的情况下，单条命令即可完成接入（安装 hook + 使用默认规则/默认配置）
- [ ] AC2: Hook 固定在 `pre-commit` 阶段触发，执行 `themis scan --platform <platform>`（默认对 `git diff --cached -U0` 的 staged 变更做 diff 扫描）
- [ ] AC3: 当命中达到阻断阈值（`severity >= critical`）时，阻断提交并给出可操作的提示（包含规则、文件、行号、脱敏预览）
- [ ] AC4: 支持豁免机制（路径/注释/baseline）在 hook 场景同样生效
- [ ] AC5: Hook 不修改用户代码，不产生网络依赖（除非明确启用）
- [ ] AC6: Hook 性能要求：只处理 staged diff 的新增/修改行；跳过二进制与超大文件；不应明显拖慢 commit（待量化）

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
- [ ] 1. **测试**：`install-hooks` 合并现有 `pre-commit` 的策略
- [ ] 2. **测试**：`git diff --cached -U0` 输入解析与 staged 行筛选
- [ ] 3. **测试**：阻断阈值（critical）与退出码打通
- [ ] 4. **实现**：`install-hooks` 合并逻辑与安装脚本生成
- [ ] 5. **实现**：获取 staged diff 并调用 `themis scan --platform`
- [ ] 6. **实现**：阻断阈值与 CLI 退出码联动
- [ ] 7. **重构**：抽离 hook 安装/执行公共逻辑
- [ ] 8. **测试**：端到端（临时 git repo 中提交包含样本 secret 的 staged 变更应被阻断）

## 6. 约束与依赖关系 (Constraints & Dependencies)
- 约束：hook 必须轻量，不显著拖慢 commit；不引入网络依赖
- 依赖：依赖 SS001 CLI 与 SS002 diff 解析能力

## 7. 图表 (可选) (Diagrams (Optional))
（无）

## 8. 开发笔记与日志 (Development Notes & Log)
- 2026-01-29 - AI: Story 草稿，待确认 hook 覆盖策略与阻断阈值配置项命名。

## 9. AI 交互日志 (Chat Command Log - AI Interaction Record)
- 用户: 工具只需要支持 commit 与 merge request 两个节点；commit 严重命中要阻断提交（默认仅 critical）；MR 使用 GitLab CI 回写 discussion；多仓多平台各自配置文件。
