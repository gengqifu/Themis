---
title: "SS003 - GitLab MR 集成（回写 review comment/讨论）"
id: "SS003"
target_version: "v0.2"
status: "已批准"
owner: "AI 助手"
story_points: "TBD"
jira_id: ""
created_date: "2026-01-29"
last_updated: "2026-01-29"
related_prd_feature: "../index.md"
---

## 1. 用户故事描述 (User Story Description)
**作为一个** 代码仓库管理员/安全负责人  
**我想要** 使用 GitLab CI 在 Merge Request 创建/更新时触发扫描，并把结果以 review comment/讨论的形式回写到 MR  
**以便于** 让 reviewer 看到明确的风险与建议（当前不阻断合并）

## 2. 验收标准 (Acceptance Criteria - AC)
- [ ] AC1: 使用 GitLab CI 的 MR pipeline 触发扫描（opened/updated）
- [ ] AC2: 获取 MR diff（CI 提供的 MR diff 或 GitLab API），并使用 `diff` 模式扫描
- [ ] AC3: 将扫描结果回写到 MR 的 **discussion**（仅 discussion），并更新同一条 discussion
- [ ] AC4: 回写内容默认脱敏，避免泄露（不写入完整 secret）

## 3. 背景与上下文 (Context & Background)
- 使用 GitLab CI 在 MR 阶段触发扫描；当前未开通“阻断 MR 合并”的能力，因此本 Story 的目标是“回写 comment/讨论”，不做阻断。

## 4. 技术设计与实现计划 (Technical Design & Implementation Plan)

### 4.1. 提议的解决方案/方法 (Proposed Solution / Approach)
候选集成方式（已确定使用 GitLab CI）：
- 在 CI job 中运行 `themis scan --diff`（基于 CI 提供的 MR diff 信息或 API 拉取）
- 使用 GitLab API 回写 MR discussion（固定更新同一条 discussion，避免重复）

### 4.2. 安全性考量
- GitLab token 权限最小化：只需读取 MR diff + 写入 MR 评论/状态
- 扫描结果脱敏与限量（避免刷屏与二次泄露）

## 5. 任务 (TDD 聚焦) (Tasks (TDD Focused))
- [ ] 1. **测试**：MR pipeline 变量解析与 diff 获取逻辑
- [ ] 2. **测试**：discussion 回写（更新同一条 discussion）
- [ ] 3. **测试**：CI 运行输出（脱敏、格式正确）
- [ ] 4. **实现**：CI job 触发条件与必要变量（MR pipeline）
- [ ] 5. **实现**：GitLab API 客户端（获取 MR diff、回写 discussion）
- [ ] 6. **实现**：集成扫描器并生成 MR 友好的输出
- [ ] 7. **重构**：抽离 CI/MR 适配层，减少耦合
- [ ] 8. **测试**：端到端（本地模拟 CI 环境 + mock GitLab API）

## 6. 待解决问题 (Open Questions)
- GitLab 为 self-managed，版本 13.5.3。
- discussion 的更新策略：更新同一条 discussion。

## 7. 图表 (可选) (Diagrams (Optional))
（无）

## 8. 开发笔记与日志 (Development Notes & Log)
- 2026-01-29 - AI: Story 草稿，按“GitLab CI 触发 + MR 评论回写、不阻断合并”的方案整理。

## 9. AI 交互日志 (Chat Command Log - AI Interaction Record)
- 用户: GitLab 为 self-managed；MR 使用 GitLab CI 触发扫描；回写方式仅 discussion；不阻断合并；commit 阶段仅 critical 阻断；多仓多平台各平台独立配置文件；输出默认脱敏且可配置开关。
