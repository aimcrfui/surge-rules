#!/usr/bin/env python3
"""Validate personal Surge rules and the ordered rule snippet."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PERSONAL_ROOT = ROOT / "rules" / "personal"
SNIPPET_PATH = ROOT / "surge-rule-snippet.conf"

IP_TYPES = {"IP-CIDR", "IP-CIDR6", "GEOIP", "IP-ASN"}
NON_IP_TYPES = {
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "DOMAIN-WILDCARD",
    "PROCESS-NAME",
    "DEST-PORT",
    "SRC-PORT",
    "IN-PORT",
    "PROTOCOL",
    "URL-REGEX",
    "USER-AGENT",
}
LOGICAL_TYPES = {"AND", "OR", "NOT"}
POLICIES = {
    "DIRECT",
    "REJECT",
    "REJECT-DROP",
    "REJECT-NO-DROP",
    "REJECT-TINYGIF",
    "Home",
    "Telegram",
    "AIGC",
    "Stream",
    "Foreign",
    "in",
}
EXPECTED_POLICY = {
    "reject": {"REJECT", "REJECT-DROP"},
    "direct": {"DIRECT"},
    "home": {"Home"},
    "telegram": {"Telegram"},
    "ai": {"AIGC"},
    "stream": {"Stream"},
    "foreign": {"Foreign"},
    "in": {"in"},
}


def active_lines(path: Path) -> list[tuple[int, str]]:
    return [
        (line_number, value)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if (value := line.strip()) and not value.startswith(("#", "//"))
    ]


def validate_personal_files(errors: list[str]) -> None:
    occurrences: dict[str, list[str]] = defaultdict(list)

    for layer in ("non_ip", "ip"):
        directory = PERSONAL_ROOT / layer
        for path in sorted(directory.glob("*.list")):
            if path.stem not in EXPECTED_POLICY:
                errors.append(f"{path}: filename does not map to a known policy")

            seen: set[str] = set()
            for line_number, rule in active_lines(path):
                location = f"{path.relative_to(ROOT)}:{line_number}"
                rule_type = rule.split(",", 1)[0]

                if rule in seen:
                    errors.append(f"{location}: duplicate rule in the same file: {rule}")
                seen.add(rule)
                occurrences[rule].append(location)

                if any(rule.endswith(f",{policy}") for policy in POLICIES):
                    errors.append(f"{location}: external ruleset entries must not contain a policy")

                if layer == "ip":
                    if rule_type not in IP_TYPES:
                        errors.append(f"{location}: IP ruleset contains non-IP rule type {rule_type}")
                elif rule_type in IP_TYPES:
                    errors.append(f"{location}: non-IP ruleset contains IP rule type {rule_type}")
                elif rule_type not in NON_IP_TYPES | LOGICAL_TYPES:
                    errors.append(f"{location}: unsupported personal rule type {rule_type}")

    for rule, locations in occurrences.items():
        if len(locations) > 1:
            errors.append(f"personal rule appears in multiple policy files: {rule} ({', '.join(locations)})")


def rule_kind(rule: str) -> str:
    rule_type = rule.split(",", 1)[0]
    if rule_type in IP_TYPES:
        return "ip"
    if rule_type == "RULE-SET":
        if "/rules/personal/ip/" in rule or "/List/ip/" in rule:
            return "ip"
        if "/rules/personal/non_ip/" in rule or "/List/non_ip/" in rule:
            return "non_ip"
    if rule_type == "DOMAIN-SET":
        return "non_ip"
    if rule_type in NON_IP_TYPES | LOGICAL_TYPES:
        return "non_ip"
    if rule_type == "FINAL":
        return "final"
    return "other"


def validate_snippet(errors: list[str]) -> None:
    rules = active_lines(SNIPPET_PATH)
    active_rules = [(line_number, rule) for line_number, rule in rules if rule != "[Rule]"]
    seen_ip_section = False
    seen_urls: set[str] = set()

    for line_number, rule in active_rules:
        location = f"{SNIPPET_PATH.relative_to(ROOT)}:{line_number}"
        kind = rule_kind(rule)

        if kind == "ip":
            seen_ip_section = True
        elif kind == "non_ip" and seen_ip_section:
            errors.append(f"{location}: non-IP rule appears after the IP section started")

        if "/rules/personal/non_ip/" in rule and "extended-matching" not in rule:
            errors.append(f"{location}: personal non-IP ruleset must use extended-matching")

        if "/rules/personal/" in rule:
            match = re.search(r"https://raw\.githubusercontent\.com/aimcrfui/surge-rules/main/([^,]+)", rule)
            if not match:
                errors.append(f"{location}: unrecognized personal Raw URL")
                continue

            relative_path = match.group(1)
            if not (ROOT / relative_path).exists():
                errors.append(f"{location}: referenced personal file does not exist: {relative_path}")

            policy = rule.split(",")[-2] if rule.endswith(",extended-matching") else rule.rsplit(",", 1)[-1]
            filename = Path(relative_path).stem
            if policy not in EXPECTED_POLICY.get(filename, set()):
                errors.append(f"{location}: {relative_path} is assigned unexpected policy {policy}")

            if relative_path in seen_urls:
                errors.append(f"{location}: personal ruleset is referenced more than once: {relative_path}")
            seen_urls.add(relative_path)

    if not active_rules or active_rules[-1][1] != "FINAL,Foreign,dns-failed":
        errors.append(f"{SNIPPET_PATH.relative_to(ROOT)}: final active rule must be FINAL,Foreign,dns-failed")

    ordered_markers = [
        "/List/non_ip/ai.conf",
        "/List/non_ip/stream.conf",
        "/List/non_ip/global.conf",
        "/List/non_ip/domestic.conf",
        "/List/non_ip/lan.conf",
        "/List/ip/reject.conf",
        "/List/ip/telegram.conf",
        "/List/ip/stream.conf",
        "/List/ip/lan.conf",
        "/List/ip/domestic.conf",
        "/List/ip/china_ip.conf",
    ]
    positions = {}
    for marker in ordered_markers:
        positions[marker] = next(
            (index for index, (_, rule) in enumerate(active_rules) if marker in rule),
            None,
        )
        if positions[marker] is None:
            errors.append(f"{SNIPPET_PATH.relative_to(ROOT)}: missing ordered upstream rule {marker}")

    present_positions = [positions[marker] for marker in ordered_markers if positions[marker] is not None]
    if present_positions != sorted(present_positions):
        errors.append(f"{SNIPPET_PATH.relative_to(ROOT)}: upstream non-IP/IP rule ordering is invalid")


def main() -> int:
    errors: list[str] = []
    validate_personal_files(errors)
    validate_snippet(errors)

    if errors:
        print("Personal Surge rule validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    file_count = len(list(PERSONAL_ROOT.glob("*/*.list")))
    rule_count = sum(len(active_lines(path)) for path in PERSONAL_ROOT.glob("*/*.list"))
    print(f"Personal Surge rules valid: {rule_count} rules across {file_count} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
