import optuna
import pytest

from docktuna.optuna_db.optuna_db import (OptunaDatabase,
                                          temporary_optuna_verbosity)


def simple_objective(trial: optuna.Trial) -> float:
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2


@pytest.fixture
def optuna_db():
    my_db = OptunaDatabase(
        username_secret="tuning_dbs_user",
        db_password_secret="tuningdb_tuner_password",
        db_name_secret="model_tuning_db_name",
        hostname_secret="postgres_dbs_host",
    )
    my_study = my_db.get_study(study_name="test_study")
    my_study.optimize(func=simple_objective, n_trials=3)

    return my_db


def test_storage_getter(optuna_db):
    storage = optuna_db.storage
    assert storage is not None


def test_public_properties(optuna_db):
    assert optuna_db.username is not None
    assert optuna_db.db_name is not None
    assert optuna_db.hostname is not None


def test_study_summaries(optuna_db):
    study_summaries = optuna_db.study_summaries
    assert type(study_summaries) == type([])


def test_get_study(optuna_db):
    my_study = optuna_db.get_study(study_name="test_study")
    assert my_study is not None


def test_get_best_params(optuna_db):
    best_params = optuna_db.get_best_params(study_name="test_study")
    assert type(best_params) == type({})


def test_get_all_studies(optuna_db):
    all_studies = optuna_db.get_all_studies()
    assert len(all_studies) > 0


def test_num_existing_studies(optuna_db):
    assert optuna_db.num_existing_studies > 0


def test_get_last_update_time(optuna_db):
    my_study = optuna_db.get_study(study_name="test_study")
    last_update_time = OptunaDatabase.get_last_update_time(study=my_study)
    assert last_update_time is not None


def test_get_latest_study(optuna_db):
    latest_study = optuna_db.get_latest_study()
    assert latest_study.study_name == "test_study"

def test_read_bad_secret_path(optuna_db):
    with pytest.raises(Exception):
        optuna_db._read_secret("not_a_secret")

def test_is_in_db(optuna_db):
    assert optuna_db.is_in_db(study_name="test_study")

def test_no_study_summary(optuna_db):
    optuna_db.get_study(study_name="unused_study")
    best_params = optuna_db.get_best_params(study_name="unused_study")
    assert len(best_params) == 0


