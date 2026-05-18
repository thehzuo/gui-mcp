from __future__ import annotations


def byte_size(value: str) -> int:
    return len(value.encode("utf-8"))
