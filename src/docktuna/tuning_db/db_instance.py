from docktuna.tuning_db.optuna_db_new import OptunaDatabaseNew

OPTUNA_DB = None

def get_optuna_db() -> OptunaDatabaseNew:
    """Returns a global OptunaDatabaseNew instance, initializing if necessary."""
    global OPTUNA_DB
    if OPTUNA_DB is None:
        OPTUNA_DB = OptunaDatabaseNew(
            username_secret="tuning_dbs_user",
            db_password_secret="tuningdb_tuner_password",
            db_name_secret="model_tuning_db_name",
            hostname_secret="postgres_dbs_host"
        )
        try:
            _ = OPTUNA_DB.storage  # Force initialization to catch errors early
        except Exception as e:
            OPTUNA_DB = None  # Reset on failure
            raise RuntimeError(f"Failed to initialize Optuna database: {e}")
    return OPTUNA_DB



