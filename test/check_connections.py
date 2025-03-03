import sys
from pathlib import Path

# sys.path.append(str(Path(__file__).parent.parent.parent))
# import tuning_studies_database as tdb
from docktuna.tuning_db.db_instance import get_optuna_db
from docktuna.tuning_db.optuna_db_new import (
    OptunaDatabaseNew,
    # ATTACK_TUNING_DB,
)


def test_tuning_study_db(db: OptunaDatabaseNew):
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

    test_tuning_study_db(db=my_db)
    # test_tuning_study_db(db=ATTACK_TUNING_DB)
