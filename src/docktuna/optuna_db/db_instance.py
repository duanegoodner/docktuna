from dotenv import load_dotenv
from os import getenv
from pathlib import Path

from docktuna.optuna_db.optuna_db import OptunaDatabase

OPTUNA_DB = None


def get_optuna_db() -> OptunaDatabase:
    """
    Returns a global OptunaDatabase instance, initializing it if necessary.

    If the database instance does not exist, it will be created using credentials
    stored in Docker secrets. If initialization fails, an exception is raised.

    Returns:
        The global OptunaDatabase instance.

    Raises:
        RuntimeError: If the database initialization fails.
    """
    global OPTUNA_DB
    if OPTUNA_DB is None:
        dotenv_path = (
            Path.home() / "project" / "docker" / "databases" / "tuning_dbs.env"
        )
        load_dotenv(dotenv_path=dotenv_path)

        OPTUNA_DB = OptunaDatabase(
            username=getenv("TUNING_DBS_USER"),
            db_password_secret="tuningdb_tuner_password",
            db_name=getenv("MODEL_TUNING_DB_NAME"),
            hostname=getenv("POSTGRES_DBS_HOST"),
        )
        try:
            _ = OPTUNA_DB.storage  # Force initialization to catch errors early
        except Exception as e:
            OPTUNA_DB = None  # Reset on failure
            raise RuntimeError(f"Failed to initialize Optuna database: {e}")
    return OPTUNA_DB
