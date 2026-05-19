from __future__ import annotations

from copy import deepcopy
from typing import Any


class JsonPatchError(ValueError):
    pass


def apply_json_patch(document: dict[str, Any], patch: list[Any]) -> dict[str, Any]:
    data = deepcopy(document)
    for op in patch:
        op_name = getattr(op, "op", None) or op.get("op")
        path = getattr(op, "path", None) or op.get("path")
        value = getattr(op, "value", None) if hasattr(op, "value") else op.get("value")
        if not isinstance(path, str) or not path.startswith("/"):
            raise JsonPatchError(f"Invalid JSON pointer path: {path!r}")
        parent, token = _resolve_parent(data, path)
        if op_name == "add":
            _add(parent, token, value)
        elif op_name == "replace":
            _replace(parent, token, value)
        elif op_name == "remove":
            _remove(parent, token)
        else:
            raise JsonPatchError(f"Unsupported patch operation: {op_name!r}")
    return data


def _tokens(path: str) -> list[str]:
    return [part.replace("~1", "/").replace("~0", "~") for part in path.split("/")[1:]]


def _resolve_parent(document: Any, path: str) -> tuple[Any, str]:
    tokens = _tokens(path)
    if not tokens:
        raise JsonPatchError("Patch path must point inside the document")
    current = document
    for token in tokens[:-1]:
        current = _get(current, token)
    return current, tokens[-1]


def _get(container: Any, token: str) -> Any:
    if isinstance(container, list):
        try:
            return container[int(token)]
        except (ValueError, IndexError) as exc:
            raise JsonPatchError(f"List index not found: {token}") from exc
    if isinstance(container, dict):
        if token not in container:
            raise JsonPatchError(f"Object key not found: {token}")
        return container[token]
    raise JsonPatchError(f"Cannot traverse into {type(container).__name__}")


def _add(parent: Any, token: str, value: Any) -> None:
    if isinstance(parent, list):
        if token == "-":
            parent.append(value)
            return
        try:
            index = int(token)
        except ValueError as exc:
            raise JsonPatchError(f"Invalid list index: {token}") from exc
        if index < 0 or index > len(parent):
            raise JsonPatchError(f"List add index out of range: {token}")
        parent.insert(index, value)
        return
    if isinstance(parent, dict):
        parent[token] = value
        return
    raise JsonPatchError(f"Cannot add into {type(parent).__name__}")


def _replace(parent: Any, token: str, value: Any) -> None:
    if isinstance(parent, list):
        try:
            parent[int(token)] = value
        except (ValueError, IndexError) as exc:
            raise JsonPatchError(f"List index not found: {token}") from exc
        return
    if isinstance(parent, dict):
        if token not in parent:
            raise JsonPatchError(f"Object key not found: {token}")
        parent[token] = value
        return
    raise JsonPatchError(f"Cannot replace in {type(parent).__name__}")


def _remove(parent: Any, token: str) -> None:
    if isinstance(parent, list):
        try:
            del parent[int(token)]
        except (ValueError, IndexError) as exc:
            raise JsonPatchError(f"List index not found: {token}") from exc
        return
    if isinstance(parent, dict):
        if token not in parent:
            raise JsonPatchError(f"Object key not found: {token}")
        del parent[token]
        return
    raise JsonPatchError(f"Cannot remove from {type(parent).__name__}")
