---
title: "产品需求文档 (PRD) - Themis 项目概览"
version: 1.0.0
last_updated: 2026-01-29
status: "已批准"
---

## 1. 引言
Themis 是一个用于扫描代码仓库中潜在安全隐患的工具。本 PRD 索引文档聚焦于“敏感信息/密钥泄露检测”能力，并作为各 Feature PRD 的入口。

## 2. 核心文档链接
- **整体愿景与长期目标**: [./APP-Overall-Vision.md](./APP-Overall-Vision.md)

## 3. 当前项目状态与高层路线图
- **当前焦点**: 在 `git commit` 阶段对严重命中（仅 `critical`）进行阻断；在 Merge Request 阶段通过 GitLab CI 触发扫描并以 review comment/讨论形式告警（当前不阻断合并）。
- **后续主要里程碑**:
  - v0.1: 可用的规则/配置系统 + CLI 扫描（diff/全量）+ 输出（脱敏）+ Git commit 阶段阻断（git hook）
  - v0.2: GitLab Merge Request 集成（MR 触发扫描 + 结果回写为 review comment/讨论；不阻断合并）
  - v0.3: 规则库完善（GP/GCP、常见 token、弱口令等）+ baseline/豁免体验优化

## 4. Feature (特性/Epic) 概览与状态

### 4.1. Feature: Secret & Sensitive Info Scanning（敏感信息扫描）
- **描述**: 在 MR 阶段自动扫描新增/变更代码中的敏感信息（默认包含 Google Play/GCP 相关 key），支持可配置规则与豁免，并输出扫描结果。
- **状态**: 草稿
- **详细 PRD**: [./features/secret-scanning/index.md](./features/secret-scanning/index.md)

## 5. 关键干系人 (Stakeholders)
- 产品负责人 (Product Owner): {待补充}
- 技术负责人 (Lead Engineer): {待补充}

## 6. 文档约定
- 所有 PRD/Feature/Story 文档使用 YAML Front Matter 的 `status` 字段追踪状态（草稿/已批准/进行中/已阻塞/已完成）。

## 7. 批注 (Review Notes)
- `APP-Overall-Vision.md` 已标记为 `status: 已批准`，下一步可考虑将本索引 `status` 提升为 `已批准` 以解锁后续流程。
- 当前 Feature `secret-scanning` 仍为 `草稿`：建议补齐并确认“严重命中”阈值（例如仅 `critical` 阻断 commit）与 MR 回写方式（comment/discussion）。
- 按 `.ai/801-workflow-agile.mdc`，在 Feature/Story 进入开发前需要有全局架构文档 `.ai/architecture/arch-overview.md` 且 `status: 已批准`（当前尚未创建）。
- 干系人信息（PO/技术负责人）待补充，用于后续决策与审批责任明确。
