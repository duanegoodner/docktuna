
from docktuna.optuna_db.db_instance import get_optuna_db
from docktuna.optuna_db.optuna_db import OptunaDatabase


def check_for_tuning_studies(db: OptunaDatabase):
    try:
        tuning_studies = db.get_all_studies()
        print(
            f"Successfully checked for existing studies in:\n"
            f"\tDatabase {db.db_name} on host {db.hostname} as user {db.username}.\n"
            f"\tNumber studies found = {len(tuning_studies)}"
        )
    except Exception as e:
        print(e)


if __name__ == "__main__":
    my_db = get_optuna_db()

    check_for_tuning_studies(db=my_db)
