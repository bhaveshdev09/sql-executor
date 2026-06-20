Usage
=====

SQL Server
----------

.. code-block:: python

   from sql_executor import SqlServerExecutor, DatabaseError

   db = SqlServerExecutor(connstring="DRIVER={ODBC Driver 17 for SQL Server};...")

   # Stored procedure
   rows = db.call_procedure("dbo.GetIncidents", params=("2026-06-01",), fetch=True)

   # Raw SQL
   db.execute("UPDATE dbo.Logs SET status = ? WHERE id = ?", params=("done", 42))

   # Stream large result sets in chunks instead of loading everything into memory
   for row in db.stream_procedure("dbo.GetBigReport", chunk_size=1000):
       process(row)

   try:
       db.execute("DELETE FROM dbo.Logs WHERE id = ?", params=(42,))
   except DatabaseError:
       # Always raised on failure — never swallowed as None/False.
       raise

Adding a new backend
---------------------

Subclass :class:`sql_executor.BaseSqlExecutor` and implement two methods:

.. code-block:: python

   import psycopg2
   from sql_executor import BaseSqlExecutor

   class PostgresExecutor(BaseSqlExecutor):
       driver_error = psycopg2.Error

       def __init__(self, dsn: str):
           self.dsn = dsn

       def _connect(self):
           return psycopg2.connect(self.dsn)

       def _call_procedure_sql(self, sp_name, params):
           placeholders = ",".join("%s" for _ in params)
           return f"CALL {sp_name}({placeholders})"

``call_procedure``, ``execute``, ``stream``, and ``stream_procedure``
all come for free from the base class.

Testing
-------

.. code-block:: python

   from sql_executor import FakeExecutor

   fake = FakeExecutor()
   fake.register("dbo.GetIncidents", lambda since: [{"id": 1, "since": since}])
   fake.call_procedure("dbo.GetIncidents", params=("2026-06-01",), fetch=True)
