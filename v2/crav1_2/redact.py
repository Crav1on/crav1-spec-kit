"""Secret redaction, the same rule as 1.x sources: remove the value, keep the kind.

Personal data that is not a secret is left for the note. A secret is never a choice.
"""

from __future__ import annotations

import re

_PRIVATE_KEY = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
    re.S,
)
_ACCESS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
_BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}")
_SLACK = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")
_SK = re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")
_ASSIGN = re.compile(r"(?i)\b(api[_-]?key|password|secret|token)\s*[:=]\s*\S+")


def redact_text(text: str) -> tuple[str, list[str]]:
    kinds: list[str] = []

    def take(kind: str, replacement: str):
        def swap(_match: re.Match[str]) -> str:
            kinds.append(kind)
            return replacement

        return swap

    def assign(match: re.Match[str]) -> str:
        kinds.append("secret")
        raw = match.group(0)
        parts = re.split(r"([:=])", raw, maxsplit=1)
        if len(parts) == 3:
            return f"{parts[0]}{parts[1]}[redacted: secret]"
        return "[redacted: secret]"

    text = _PRIVATE_KEY.sub(take("private-key", "[redacted: private-key]"), text)
    text = _ACCESS_KEY.sub(take("access-key", "[redacted: access-key]"), text)
    text = _BEARER.sub(take("token", "Bearer [redacted: token]"), text)
    text = _SLACK.sub(take("token", "[redacted: token]"), text)
    text = _SK.sub(take("token", "[redacted: token]"), text)
    text = _ASSIGN.sub(assign, text)
    return text, sorted(set(kinds))


def redact_bytes(data: bytes) -> tuple[bytes, list[str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        return data, []
    redacted, kinds = redact_text(text)
    if not kinds:
        return data, []
    return redacted.encode("utf-8"), kinds
