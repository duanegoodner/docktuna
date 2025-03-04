from unittest.mock import PropertyMock, patch

import pytest

from docktuna.optuna_db.db_instance import get_optuna_db


@pytest.fixture(autouse=True)
def reset_global_optuna_db():
    """Ensures get_optuna_db() always starts fresh for each test."""
    get_optuna_db.__globals__["OPTUNA_DB"] = None


def test_get_optuna_db():
    """get_optuna_db() initializes correctly."""
    db = get_optuna_db()
    assert db is not None  # Ensure initialization works


def test_get_optuna_db_twice():
    db_a = get_optuna_db()
    db_b = get_optuna_db()


def test_get_optuna_db_failure():
    """get_optuna_db() properly handles database initialization failure."""

    with patch(
        "docktuna.optuna_db.db_instance.OptunaDatabase"
    ) as MockOptunaDatabase:
        mock_instance = MockOptunaDatabase.return_value
        # Force `.storage` to raise an exception when accessed
        type(mock_instance).storage = PropertyMock(
            side_effect=Exception("DB connection failed")
        )

        # Ensure a fresh start
        get_optuna_db.__globals__["OPTUNA_DB"] = None

        with pytest.raises(
            RuntimeError,
            match="Failed to initialize Optuna database: DB connection failed",
        ):
            get_optuna_db()  # Should raise RuntimeError

        # Ensure OPTUNA_DB was reset to None after failure
        assert get_optuna_db.__globals__["OPTUNA_DB"] is None
