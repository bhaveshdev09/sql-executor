"""Backend-agnostic base for stored-procedure / SQL executors.

Template Method pattern: this class owns everything that's the same
across DB backends (cursor lifecycle, commit/rollback, fetch-to-dict,
chunked streaming, error wrapping). A subclass only has to implement:

  - _connect()              -> open a DB-API 2.0 connection
  - _call_procedure_sql()   -> dialect-specific "call this SP" string

Everything else (call_procedure, execute, stream, stream_procedure) is
inherited for free. See sqlserver.py for a ~15-line concrete example.
"""

from __future__ import annotations

import abc
import logging
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Sequence

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Raised when a stored procedure / SQL execution fails.

    Callers should catch this rather than checking for None/False —
    it's always raised on failure, never swallowed.
    """


def _rows_to_dicts(cursor) -> List[Dict[str, Any]]:
    columns = [col[0].lower() for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class BaseSqlExecutor(abc.ABC):
    # Subclass should override with their driver's exception type,
    # e.g. `pyodbc.Error`, `psycopg2.Error`, `cx_Oracle.Error`.
    # Left as plain Exception here so a forgetful subclass still works,
    # just with a less precise catch.
    driver_error: type = Exception

    # ---- subclasses must implement -------------------------------------
    @abc.abstractmethod
    def _connect(self):
        """Return a new DB-API 2.0 connection."""

    @abc.abstractmethod
    def _call_procedure_sql(self, sp_name: str, params: Sequence[Any]) -> str:
        """Return the dialect-specific SQL string to call a stored procedure."""

    # ---- shared cursor lifecycle ----------------------------------------
    @contextmanager
    def _get_cursor(self):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _run(self, sql: str, params: Sequence[Any], fetch: bool):
        try:
            with self._get_cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                return _rows_to_dicts(cursor) if fetch else True
        except self.driver_error as db_ex:
            logger.exception("DB error executing: %s", sql)
            raise DatabaseError(str(db_ex)) from db_ex

    # ---- public API ----------------------------------------------------
    def call_procedure(
        self, sp_name: str, params: Sequence[Any] = (), fetch: bool = False
    ):
        sql = self._call_procedure_sql(sp_name, params)
        return self._run(sql, tuple(params), fetch)

    def execute(self, sql: str, params: Sequence[Any] = (), fetch: bool = False):
        """Run raw SQL (SELECT/INSERT/UPDATE/DELETE)."""
        return self._run(sql, tuple(params), fetch)

    def stream(
        self,
        sql: str,
        params: Sequence[Any] = (),
        chunk_size: int = 500,
    ) -> Iterator[Dict[str, Any]]:
        """Yield rows in chunks — for big SELECTs or SPs returning lots of rows."""
        try:
            with self._get_cursor() as cursor:
                cursor.arraysize = chunk_size
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                columns = [col[0].lower() for col in cursor.description]

                while True:
                    rows = cursor.fetchmany(chunk_size)
                    if not rows:
                        break
                    for row in rows:
                        yield dict(zip(columns, row))
        except self.driver_error as db_ex:
            logger.exception("DB error streaming: %s", sql)
            raise DatabaseError(str(db_ex)) from db_ex

    def stream_procedure(
        self, sp_name: str, params: Sequence[Any] = (), chunk_size: int = 500
    ) -> Iterator[Dict[str, Any]]:
        sql = self._call_procedure_sql(sp_name, params)
        yield from self.stream(sql, tuple(params), chunk_size)
