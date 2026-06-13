# Deployment Record

## 2026-06-13

- Reason: replace the broad locally merged rule mirrors with an ordered personal override layer plus direct Sukka upstream references.
- Live change: replaced only the active Surge Mac profile `[Rule]` section with `surge-rule-snippet.conf`.
- Rollback: restore the `[Rule]` section from `/tmp/surge-profile-before-personal-rules.conf`.
- Verification:
  - Surge native profile check returned `OK`.
  - Non-rule profile sections were unchanged.
  - All 38 external ruleset/domainset resources reported `ready`.
  - No non-IP rule appears after the IP section starts.
  - Final active rule is `FINAL,Foreign,dns-failed`.
