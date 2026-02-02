# Themis
用来扫描代码中潜在的安全隐患

## 本地 commit hook
- 安装：
  - `python -m themis install-hooks --platform backend --repo-root .`
- 卸载：
  - `python -m themis uninstall-hooks --repo-root .`

## GitLab MR 集成示例
- 参考 `.gitlab-ci.yml.example`，可在 `merge_request_event` 时触发扫描并回写同一条 discussion。
- 示例默认使用 `backend` 平台配置，可按仓库类型改为 `android` / `ios` / `web`。

必需环境变量（在 GitLab CI/CD Variables 配置）：
- `GITLAB_TOKEN`（建议使用 masked + protected，最小权限）
- `CI_PROJECT_ID`
- `CI_MERGE_REQUEST_IID`
- `CI_API_V4_URL`

说明：
- `CI_PROJECT_ID`、`CI_MERGE_REQUEST_IID`、`CI_API_V4_URL` 由 GitLab CI 自动注入。
- `GITLAB_TOKEN` 需手动在仓库或组级变量中配置。
