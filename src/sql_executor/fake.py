"""In-memory test double — no real DB connection involved."""

from __future__ import annotations

from typing import Any, Callable, Dict, Sequence

from .base import BaseSqlExecutor


class FakeExecutor(BaseSqlExecutor):
    """Register a Python callable per stored-procedure name and call it
    just like the real thing, for unit tests.

        fake = FakeExecutor()
        fake.register("dbo.GetIncidents", lambda since: [{"id": 1}])
        fake.call_procedure("dbo.GetIncidents", params=("2026-06-01",), fetch=True)
    """

    driver_error = Exception

    def __init__(self):
        self.handlers: Dict[str, Callable[..., Any]] = {}

    def register(self, sp_name: str, handler: Callable[..., Any]):
        self.handlers[sp_name] = handler

    def _connect(self):
        raise NotImplementedError("FakeExecutor never opens a real connection")

    def _call_procedure_sql(self, sp_name: str, params: Sequence[Any]) -> str:
        # Unused — call_procedure is overridden below instead of going
        # through _run()/_connect(), since there's no real cursor here.
        return sp_name

    def call_procedure(
        self, sp_name: str, params: Sequence[Any] = (), fetch: bool = False
    ):
        if sp_name not in self.handlers:
            raise ValueError(f"No handler registered for {sp_name!r}")
        result = self.handlers[sp_name](*params)
        return result if fetch else True

    def execute(self, sql: str, params: Sequence[Any] = (), fetch: bool = False):
        raise NotImplementedError("FakeExecutor only fakes stored procedures")
