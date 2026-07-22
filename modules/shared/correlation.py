from __future__ import annotations

from contextvars import ContextVar
from uuid import uuid4

_correlation_id: ContextVar[str | None] = ContextVar(
    "all_in_one_correlation_id", default=None
)


def new_correlation_id() -> str:
    return str(uuid4())


def set_correlation_id(correlation_id: str | None = None) -> str:
    value = correlation_id or new_correlation_id()
    _correlation_id.set(value)
    return value


def get_correlation_id() -> str:
    current = _correlation_id.get()
    if current:
        return current
    return set_correlation_id()
