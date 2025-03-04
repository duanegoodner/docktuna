import dotenv
import optuna
import pytest
from pathlib import Path
from dotenv import load_dotenv
from os import getenv

from docktuna.optuna_db.optuna_db import (
    OptunaDatabase,
    temporary_optuna_verbosity,
)


def simple_objective(trial: optuna.Trial) -> float:
    """
    Defines a simple objective function for testing.

    This function optimizes the quadratic function (x - 2)^2.

    Args:
        trial: An Optuna trial object.

    Returns:
        The loss value to be minimized.
    """
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2


@pytest.fixture
def optuna_db():
    """
    Creates an OptunaDatabase instance and runs a test study.

    Returns:
        An initialized OptunaDatabase instance.
    """
    dotenv_path = (
        Path.home() / "project" / "docker" / "databases" / "tuning_dbs.env"
    )
    load_dotenv(dotenv_path=dotenv_path)
    my_db = OptunaDatabase(
        username=getenv("TUNING_DBS_USER"),
        db_password_secret="optuna_db_user_password",
        db_name=getenv("MODEL_TUNING_DB_NAME"),
        hostname=getenv("POSTGRES_DBS_HOST"),
    )
    my_study = my_db.get_study(study_name="test_study")
    my_study.optimize(func=simple_objective, n_trials=3)

    return my_db


def test_storage_getter(optuna_db):
    """Storage property is accessible."""
    storage = optuna_db.storage
    assert storage is not None


def test_public_properties(optuna_db):
    """Username, db_name, and hostname are accessible."""
    assert optuna_db.username is not None
    assert optuna_db.db_name is not None
    assert optuna_db.hostname is not None


def test_study_summaries(optuna_db):
    """Study summaries return a list."""
    study_summaries = optuna_db.study_summaries
    assert isinstance(study_summaries, list)


def test_get_study(optuna_db):
    """Retrieves an existing study."""
    my_study = optuna_db.get_study(study_name="test_study")
    assert my_study is not None


def test_get_best_params(optuna_db):
    """Best parameters are returned as a dictionary."""
    best_params = optuna_db.get_best_params(study_name="test_study")
    assert isinstance(best_params, dict)


def test_get_all_studies(optuna_db):
    """Retrieves all stored studies."""
    all_studies = optuna_db.get_all_studies()
    assert len(all_studies) > 0


def test_num_existing_studies(optuna_db):
    """Number of studies is greater than zero."""
    assert optuna_db.num_existing_studies > 0


def test_get_last_update_time(optuna_db):
    """Retrieves the last update time of a study."""
    my_study = optuna_db.get_study(study_name="test_study")
    last_update_time = OptunaDatabase.get_last_update_time(study=my_study)
    assert last_update_time is not None


def test_get_latest_study(optuna_db):
    """Retrieves the most recently updated study."""
    latest_study = optuna_db.get_latest_study()
    assert latest_study.study_name == "test_study"


def test_read_bad_secret_path(optuna_db):
    """Accessing an invalid secret path raises an exception."""
    with pytest.raises(Exception):
        optuna_db._read_secret("not_a_secret")


def test_is_in_db(optuna_db):
    """Checks if an existing study is in the database."""
    assert optuna_db.is_in_db(study_name="test_study")


def test_no_study_summary(optuna_db):
    """Retrieving best parameters from an unused study returns an empty dictionary."""
    optuna_db.get_study(study_name="unused_study")
    best_params = optuna_db.get_best_params(study_name="unused_study")
    assert len(best_params) == 0
