"""
Development file for quick OptunaDatabase checks.

This script is used for **manual debugging** outside of pytest, allowing developers 
to quickly check database connectivity and study retrieval.

Usage:
    python dev_check.py
"""

from docktuna.optuna_db.db_instance import get_optuna_db
from docktuna.optuna_db.optuna_db import OptunaDatabase


def check_for_tuning_studies(db: OptunaDatabase):
    """
    Retrieves and prints the number of existing Optuna studies in the database.

    Args:
        db: An OptunaDatabase instance.

    Prints:
        The number of studies found, along with database connection details.
    """
    try:
        tuning_studies = db.get_all_studies()
        print(
            f"Successfully checked for existing Optuna studies in:\n"
            f"\tDatabase {db.db_name} on host {db.hostname} as user {db.username}.\n"
            f"\tNumber of studies found = {len(tuning_studies)}"
        )
    except Exception as e:
        print(f"Error retrieving studies: {e}")


if __name__ == "__main__":
    """
    Initializes the Optuna database connection and checks for existing studies.
    """
    my_db = get_optuna_db()
    check_for_tuning_studies(db=my_db)
