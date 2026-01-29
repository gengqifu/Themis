---
title: "Themis - 整体愿景与长期目标"
version: 1.0.0
last_updated: 2026-01-29
status: "已批准"
---

## 1. 执行摘要 (Executive Summary)
通过在代码进入主分支之前（`git commit` 与 Merge Request 阶段）自动发现并处置敏感信息泄露风险，降低密钥外泄带来的安全、合规与经济损失。

## 2. 问题陈述 (Problem Statement)
- 代码仓库中可能被误提交 Google Play/GCP 等高敏感密钥，且难以及时发现。
- 代码形态多样（Android/Backend/Web/iOS），敏感信息可能出现在任意文件与任意位置。
- 团队希望不依赖 AI 的检测方案：在 `git commit` 阶段对严重问题进行阻断；在 MR 阶段以 review comment/讨论给出提示与建议（当前不阻断合并）。

## 3. 提议的解决方案与核心价值主张 (Proposed Solution & Core Value Proposition)
- 提供 `python3` 可运行的扫描工具（CLI/可服务化），支持：
  - MR diff 扫描为默认模式 + 可选全量扫描开关
  - 可配置的敏感信息规则库（pattern/关键字/熵阈值/文件范围）
  - 可配置豁免（路径/注释/baseline）
  - 结果输出（人类可读 + 机器可读），并对敏感内容进行脱敏展示
- 与 GitLab MR 流程集成，实现：
  - 通过 GitLab CI 在 MR 阶段触发扫描，并以 review comment/讨论形式回写结果（当前不阻断 MR 合并）
- 与本地开发流程集成，实现：
  - 在 `git commit` 阶段对严重命中进行阻断提交

## 4. 目标受众 / 用户画像 (Target Audience / User Personas)
- 开发者：提交 MR 时获得可执行的告警信息。
- 安全/平台团队：维护规则与豁免策略，减少泄露事件。

## 5. 长期愿景 (3-5年) (Long-Term Vision (3-5 Years))
- 覆盖主流密钥类型与常见误提交场景，形成可持续维护的规则库与治理流程。
- 在不显著拖慢研发效率的前提下，实现“默认安全”的提交与合并体验。

## 6. 指导原则 / 产品理念 (Guiding Principles / Product Philosophy)
- 安全优先（对高敏感信息默认阻断）
- 可配置、可扩展（规则与豁免配置化）
- 低误报、可解释（命中可追溯到规则与位置；提供 baseline 降噪）
- 不二次泄露（默认脱敏输出）
- 简单易用、傻瓜化接入（控制代码规模与复杂度；一键接入默认配置，开箱即用）

## 7. 高层成功指标 (长期) (High-Level Success Metrics (Long-Term))
- 高敏感密钥（如 GP/GCP）进入主分支的事件数趋近于 0
- 误报率与处理成本可控（例如：MR 中无效告警逐步下降）
- 扫描耗时对 MR 流程影响可接受（后续以 NFR 量化）
