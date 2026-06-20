from .base import BaseSqlExecutor, DatabaseError
from .fake import FakeExecutor

__all__ = [
    "BaseSqlExecutor",
    "DatabaseError",
    "SqlServerExecutor",
    "FakeExecutor",
]

__version__ = "0.1.0"


def __getattr__(name: str):
    # Lazy import: SqlServerExecutor pulls in pyodbc (+ system unixODBC),
    # which not every environment has (e.g. running tests with FakeExecutor
    # only). Importing it on first access keeps `from sql_executor import
    # FakeExecutor` working even if pyodbc isn't installed.
    if name == "SqlServerExecutor":
        from .sqlserver import SqlServerExecutor

        return SqlServerExecutor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
