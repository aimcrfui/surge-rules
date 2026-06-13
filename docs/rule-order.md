# Personal Surge Rule Order

The ordered rule snippet follows these principles:

1. Explicit personal non-IP overrides come first.
2. Upstream domain and non-IP rules are evaluated from specific services to broad fallbacks.
3. `global.conf` and `stream.conf` are evaluated before `domestic.conf`.
4. Every IP ruleset is placed after every non-IP ruleset.
5. `FINAL,Foreign,dns-failed` is the final active rule.

IP rules can trigger local DNS resolution when the request target is a domain. Keeping them after domain and non-IP rules allows known foreign domains to select a remote policy without local DNS resolution.

Personal IP rules live in `rules/personal/ip/`. Add `no-resolve` to an IP rule when it should only match connections that already target an IP address.

The personal layer intentionally does not copy or merge Sukka's upstream rules. Surge references those upstream files directly, preserving their category boundaries and update behavior.
