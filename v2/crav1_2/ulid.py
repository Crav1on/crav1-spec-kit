"""ULID (universally unique lexicographically sortable identifier), 26 Crockford base32 chars.

Stdlib only. The timestamp is millisecond Unix time in the high 48 bits.
"""

from __future__ import annotations

import os
import time

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_INDEX = {char: i for i, char in enumerate(ALPHABET)}


def encode(timestamp_ms: int, randomness: int) -> str:
    if timestamp_ms < 0 or timestamp_ms >= 2**48:
        raise ValueError("ULID timestamp is out of range")
    if randomness < 0 or randomness >= 2**80:
        raise ValueError("ULID randomness is out of range")
    value = (timestamp_ms << 80) | randomness
    chars = []
    for _ in range(26):
        chars.append(ALPHABET[value & 31])
        value >>= 5
    return "".join(reversed(chars))


def decode(text: str) -> tuple[int, int]:
    if not is_ulid(text):
        raise ValueError("not a ULID")
    value = 0
    for char in text:
        value = (value << 5) | _INDEX[char]
    value &= (1 << 128) - 1
    return value >> 80, value & ((1 << 80) - 1)


def is_ulid(text: str) -> bool:
    if not isinstance(text, str) or len(text) != 26:
        return False
    if text[0] not in "01234567":
        return False
    return all(char in _INDEX for char in text)


def ulid(now_ms: int | None = None) -> str:
    timestamp = int(time.time() * 1000) if now_ms is None else now_ms
    randomness = int.from_bytes(os.urandom(10), "big")
    return encode(timestamp, randomness)
