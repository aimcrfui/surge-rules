# Surge Rule Provider Comparison

Checked on 2026-06-08.

## Selected Upstream

This repository currently uses [SukkaW/Surge](https://github.com/SukkaW/Surge) through `https://ruleset.skk.moe`.

Reasons:

- Native Surge `.conf` rule output, so no platform conversion is needed.
- Compact category files are available under `List/non_ip/`.
- The provider also publishes domainset, IP, Clash, sing-box, Surfboard, Stash, and module outputs.
- The project is actively updated and licensed under AGPL-3.0.

## Comparison

| Provider | Current status | Strengths | Tradeoffs for this repo |
| --- | --- | --- | --- |
| [SukkaW/Surge](https://github.com/SukkaW/Surge) | Active, Surge-first, AGPL-3.0 | Clean Surge syntax, modern categories including AIGC and streaming, generated ruleset server | AGPL-derived rules need license awareness; the full domainset reject list is very large |
| [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) | Active, very large, GPL-2.0 | Huge service-specific catalog across Surge, Loon, Quantumult X, Clash, Stash | Better for app/service precision than small personal base rules; heavier to aggregate |
| [ACL4SSR/ACL4SSR](https://github.com/ACL4SSR/ACL4SSR) | Active, CC BY-SA 4.0 | Popular ACL/GFW/adblocking base, strong Clash ecosystem presence | Less Surge-native than Sukka for this exact use case |
| [Hackl0us/SS-Rule-Snippet](https://github.com/Hackl0us/SS-Rule-Snippet) | Active, AGPL-3.0 | Long-running curated snippets for Surge and related clients | Useful reference, but not as convenient as `ruleset.skk.moe` for daily generated category pulls |
| DivineEngine/Profiles | Historical source | Many older profiles and snippets still reference it | The GitHub repository is no longer reliably resolvable, so it is not a good primary upstream |

## Local Choice

The initial rule set intentionally stays small:

- `rules/reject.list`
- `rules/direct.list`
- `rules/ai.list`
- `rules/stream.list`
- `rules/proxy.list`

For stronger ad blocking, add a separate `DOMAIN-SET` flow instead of merging Sukka's very large `domainset/reject.conf` into `RULE-SET`.
