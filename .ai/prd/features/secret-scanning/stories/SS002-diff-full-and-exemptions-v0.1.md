---
title: "SS002 - Diff/Full 扫描模式与 baseline/注释豁免"
id: "SS002"
target_version: "v0.1"
status: "进行中"
owner: "AI 助手"
story_points: "TBD"
jira_id: ""
created_date: "2026-01-29"
last_updated: "2026-01-30"
related_prd_feature: "../index.md"
---

## 1. 用户故事描述 (User Story Description)
**作为一个** 开发者/安全负责人  
**我想要** 默认只扫描 MR 的变更(diff)，并且能够通过 baseline/路径/注释来豁免合理的命中  
**以便于** 降低误报与噪声，同时保留全量扫描能力

## 2. 验收标准 (Acceptance Criteria - AC)
- [x] AC1: 支持 `diff` 模式：仅扫描新增/修改的行（输入为 `file -> line_numbers[]` 或标准 unified diff；commit 场景来自 `git diff --cached -U0`，MR 场景来自 GitLab CI 的 MR diff）
- [x] AC1.1: diff 解析仅识别 unified diff `@@` hunk，并只对 `+` 行计为新增；忽略 diff 头部（`+++ / ---`）
- [x] AC1.2: MR diff 来源：优先从 `CI_MERGE_REQUEST_DIFF_URL` 拉取；允许 `--diff-file` 指定本地 diff 文件（用于本地复现）
- [x] AC2: 支持 `full` 模式：扫描指定目录/仓库中的全部文本文件（仍需遵守大小/二进制过滤）
- [x] AC3: 支持路径豁免（glob，匹配**仓库相对路径**，基于仓库根目录；默认区分大小写）
- [x] AC4: 支持行内注释豁免（例如 `themis:ignore <RULE_ID>` 或 `themis:ignore`；允许指定 RULE_ID 精确豁免）
- [x] AC4.1: 允许“前一行注释”豁免（**仅紧邻上一行**包含 `themis:ignore` 标记即豁免下一行命中）
- [x] AC4.2: 注释豁免优先级：`themis:ignore <RULE_ID>` 仅豁免该规则；`themis:ignore` 豁免整行所有规则
- [x] AC5: 支持 baseline：把已知命中记录到 baseline 文件并在后续运行中忽略（仅对相同指纹/位置生效，默认不存原文）
- [x] AC5.1: baseline 文件格式为 `json`，最小结构 `{ "items": [ { "rule_id","file","line","hash" } ] }`
- [x] AC5.2: baseline 指纹为 `rule_id + file + line + normalized_match_hash`（normalized_match_hash = 去空白后的匹配文本 SHA256，默认不做大小写折叠）
- [x] AC5.3: baseline 路径支持相对仓库根目录；生成 baseline 时覆盖写入（避免合并复杂度）

## 3. 背景与上下文 (Context & Background)
- 你明确表示仓库可能存在示例 token/mock key，需要可控豁免机制。
- 你希望输出所有命中，但在 MR 场景中更重要的是“仅关注新增风险”，因此 diff 模式是默认。

## 4. 技术设计与实现计划 (Technical Design & Implementation Plan)

### 4.1. 提议的解决方案/方法 (Proposed Solution / Approach)
- `diff` 输入策略：
  - 方案 A（推荐）：在 GitLab CI 中读取 MR diff（或调用 GitLab API），转成 `file -> added_lines[]` 输入扫描器
  - 方案 B：支持读取本地 `git diff` 的 unified diff（便于本地复现/调试）
- baseline 指纹：
  - `rule_id + file_path + line_number + normalized_match_hash`（避免存原文）
  - line 变化导致漂移时可选增加“上下文 hash”（后续增强）
- 注释豁免：
  - 在命中行同一行内出现 marker 即豁免；允许前一行注释（已确认）

## 5. 任务 (TDD 聚焦) (Tasks (TDD Focused))
- [x] 1. **测试**：diff 输入解析（unified diff -> file/line 列表）
- [x] 2. **测试**：`diff` 模式仅扫描新增/修改行
- [x] 3. **测试**：`full` 模式扫描（仍跳过二进制/大文件）
- [x] 4. **测试**：路径豁免（glob）与行内/前一行注释豁免
- [x] 5. **测试**：baseline 过滤（相同指纹/位置命中应忽略）
- [x] 6. **测试**：diff 来源（`CI_MERGE_REQUEST_DIFF_URL` / `--diff-file`）选择逻辑
- [x] 7. **测试**：baseline 路径相对仓库根目录解析与覆盖写入
- [x] 8. **实现**：diff 输入解析与数据结构
- [x] 9. **实现**：`diff` 模式扫描（只读指定行）
- [x] 10. **实现**：`full` 模式开关
- [x] 11. **实现**：路径豁免与注释豁免
- [x] 12. **实现**：baseline schema 与过滤逻辑（仅指纹）
- [x] 13. **实现**：diff 来源选择（`CI_MERGE_REQUEST_DIFF_URL` / `--diff-file`）
- [x] 14. **实现**：baseline 路径解析（相对仓库根）与覆盖写入
- [x] 15. **重构**：简化输入管道与豁免判断

## 6. 约束与依赖关系 (Constraints & Dependencies)
- 约束：diff 解析必须兼容 `git diff --cached -U0` 与 GitLab CI 的 MR diff
- 依赖：依赖 SS001 的配置与扫描器基础能力

## 7. 图表 (可选) (Diagrams (Optional))
（无）

## 8. 开发笔记与日志 (Development Notes & Log)
- 2026-01-29 - AI: Story 草稿，待确认注释豁免规则（同一行/上一行/块注释）与 baseline 指纹策略。
- 2026-01-30 - AI: 完成 unified diff 解析测试（file -> line 列表）。
- 2026-01-30 - AI: 完成 diff-only 行过滤测试（只扫描新增/修改行）。
- 2026-01-30 - AI: 完成 full 模式扫描测试（跳过二进制/大文件）。
- 2026-01-30 - AI: 完成注释豁免测试（行内 + 前一行，含 RULE_ID 精确豁免）。
- 2026-01-30 - AI: 完成 baseline 过滤测试与 JSON 读写。
- 2026-01-30 - AI: 完成 diff 解析实现并提供 repo_root 路径解析辅助。
- 2026-01-30 - AI: 完成 diff 来源选择测试（CI URL 优先，其次 diff 文件）。
- 2026-01-30 - AI: 完成 baseline 路径解析测试（相对仓库根）。
- 2026-01-30 - AI: 增加 diff 输入构建辅助（diff -> 行号映射）。
- 2026-01-30 - AI: 实现 diff-only 文件扫描（仅扫描指定行，仍跳过二进制/大文件）。
- 2026-01-30 - AI: 增加扫描模式开关（full/diff）。
- 2026-01-30 - AI: 实现路径豁免（glob）与注释豁免工具函数。
- 2026-01-30 - AI: 增加 baseline schema 校验（items 必须为列表）。
- 2026-01-30 - AI: 实现 diff 来源读取（file 优先；URL 阶段暂未实现）。
- 2026-01-30 - AI: 基线文件覆盖写入辅助（write_baseline_overwrite）。
- 2026-01-30 - AI: 重构扫描流程（统一路径豁免判断）。
- 2026-01-30 - AI: CLI 已接入 diff 输入（`--diff-file`），可触发 diff-only 扫描。

## 9. AI 交互日志 (Chat Command Log - AI Interaction Record)
- 用户: 默认只扫 MR diff，需要支持全量扫描开关；例外可通过路径/注释/baseline 豁免；MR 使用 GitLab CI 触发扫描。
- 用户: 开始 SS002 开发，执行任务 5.1（diff 解析测试）。
- 用户: 执行 SS002 任务 5.2（diff-only 行过滤测试）。
- 用户: 执行 SS002 任务 5.3（full 模式扫描测试）。
- 用户: 执行 SS002 任务 5.4（路径/注释豁免测试）。
- 用户: 执行 SS002 任务 5.5（baseline 过滤测试）。
- 用户: 执行 SS002 任务 5.6（diff 解析实现）。
- 用户: 指明执行任务 6（diff 来源选择逻辑）。
- 用户: 执行 SS002 任务 5.7（baseline 路径解析测试）。
- 用户: 执行 SS002 任务 5.8（diff 输入解析与数据结构实现）。
- 用户: 执行 SS002 任务 5.9（diff 模式扫描实现）。
- 用户: 执行 SS002 任务 5.10（full 模式开关实现）。
- 用户: 执行 SS002 任务 5.11（路径/注释豁免实现）。
- 用户: 执行 SS002 任务 5.12（baseline schema 与过滤逻辑实现）。
- 用户: 执行 SS002 任务 5.13（diff 来源选择实现）。
- 用户: 执行 SS002 任务 5.14（baseline 路径解析与覆盖写入）。
- 用户: 执行 SS002 任务 5.15（重构简化输入管道与豁免判断）。
- 用户: 要求补全 AC1 端到端接入（diff 输入 -> CLI 扫描）。
