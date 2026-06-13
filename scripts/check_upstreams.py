#!/usr/bin/env python3
"""Check that every upstream ruleset is reachable and structurally healthy."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVIDERS_PATH = ROOT / "sources" / "providers.json"
IP_TYPES = {"IP-CIDR", "IP-CIDR6", "GEOIP", "IP-ASN"}
SUKKA_MARKER = "DOMAIN,7h1s_rul35et_i5_mad3_by_5ukk4w-ruleset.skk.moe"


def active_lines(text: str) -> list[str]:
    return [
        value
        for line in text.splitlines()
        if (value := line.strip()) and not value.startswith(("#", "//"))
    ]


def check_provider(provider: dict[str, object]) -> tuple[str, int]:
    request = urllib.request.Request(
        str(provider["url"]),
        headers={"User-Agent": "aimcrfui-surge-rules-health-check/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "")
            text = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"{provider['name']}: fetch failed: {exc}") from exc

    if "html" in content_type.lower() or "<html" in text[:500].lower():
        raise RuntimeError(f"{provider['name']}: upstream returned HTML instead of a ruleset")

    rules = active_lines(text)
    minimum = int(provider["min_rules"])
    if len(rules) < minimum:
        raise RuntimeError(f"{provider['name']}: only {len(rules)} rules, expected at least {minimum}")

    kind = provider["kind"]
    if kind == "domainset":
        invalid = [rule for rule in rules if "," in rule]
    elif kind == "ip":
        invalid = [
            rule
            for rule in rules
            if rule != SUKKA_MARKER and rule.split(",", 1)[0] not in IP_TYPES
        ]
    elif kind == "non_ip":
        invalid = [
            rule
            for rule in rules
            if rule.split(",", 1)[0] in IP_TYPES and not rule.endswith(",no-resolve")
        ]
    else:
        raise RuntimeError(f"{provider['name']}: unknown provider kind {kind}")

    if invalid:
        raise RuntimeError(f"{provider['name']}: unexpected rule structure: {invalid[0]}")

    return str(provider["name"]), len(rules)


def main() -> int:
    providers = json.loads(PROVIDERS_PATH.read_text(encoding="utf-8"))["providers"]
    errors: list[str] = []
    results: list[tuple[str, int]] = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(check_provider, provider): provider for provider in providers}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except RuntimeError as exc:
                errors.append(str(exc))

    if errors:
        print("Upstream Surge rule health check failed:", file=sys.stderr)
        for error in sorted(errors):
            print(f"- {error}", file=sys.stderr)
        return 1

    for name, count in sorted(results):
        print(f"{name}: {count} rules")
    print(f"Upstream Surge rules healthy: {len(results)} providers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
