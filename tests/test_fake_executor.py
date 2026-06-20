import pytest

from sql_executor import FakeExecutor


def test_call_procedure_fetch():
    fake = FakeExecutor()
    fake.register("dbo.GetIncidents", lambda since: [{"id": 1, "since": since}])

    result = fake.call_procedure(
        "dbo.GetIncidents", params=("2026-06-01",), fetch=True
    )

    assert result == [{"id": 1, "since": "2026-06-01"}]


def test_call_procedure_no_fetch_returns_true():
    fake = FakeExecutor()
    fake.register("dbo.DoThing", lambda: None)

    assert fake.call_procedure("dbo.DoThing") is True


def test_unregistered_sp_raises():
    fake = FakeExecutor()
    with pytest.raises(ValueError):
        fake.call_procedure("dbo.Unknown")


def test_execute_not_implemented():
    fake = FakeExecutor()
    with pytest.raises(NotImplementedError):
        fake.execute("SELECT 1")
