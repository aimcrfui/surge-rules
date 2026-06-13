# Deployment Record

## 2026-06-13

- Reason: replace the broad locally merged rule mirrors with an ordered personal override layer plus direct Sukka upstream references.
- Repository change: created and published the candidate personal rule structure and ordered snippet.
- Live status: not deployed. A temporary `[Rule]` replacement was fully rolled back at the user's request.
- Rollback verification: the active Surge original profile exactly matched `/tmp/surge-profile-before-personal-rules.conf`, with zero `aimcrfui/surge-rules` references.
- Verification:
  - Surge native profile check returned `OK`.
  - Repository validation and upstream health checks passed.
  - GitHub Actions validation passed.
