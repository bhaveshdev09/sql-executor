"""SQL Server backend — the only piece that knows about pyodbc."""

from __future__ import annotations

from typing import Any, Sequence

import pyodbc

from .base import BaseSqlExecutor


class SqlServerExecutor(BaseSqlExecutor):
    """Stored-procedure / SQL executor for SQL Server, backed by pyodbc."""

    driver_error = pyodbc.Error

    def __init__(self, connstring: str):
        self.connstring = connstring

    def _connect(self):
        return pyodbc.connect(self.connstring)

    def _call_procedure_sql(self, sp_name: str, params: Sequence[Any]) -> str:
        placeholders = ",".join("?" for _ in params)
        return f"EXEC {sp_name} {placeholders}".strip()
