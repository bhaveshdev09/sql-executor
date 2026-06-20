sql-executor
============

Backend-agnostic stored-procedure / SQL executor. ``BaseSqlExecutor``
owns connection lifecycle, commit/rollback, fetch-to-dict, chunked
streaming, and error wrapping. A new backend only implements two
methods.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   api

Quick example
-------------

.. code-block:: python

   from sql_executor import SqlServerExecutor

   db = SqlServerExecutor(connstring="DRIVER={ODBC Driver 17 for SQL Server};...")

   rows = db.call_procedure("dbo.GetIncidents", params=("2026-06-01",), fetch=True)

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
