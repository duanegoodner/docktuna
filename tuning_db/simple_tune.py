import logging
import sys

import optuna

import tuning_studies_database as tsd

# Add stream handler of stdout to show the messages
optuna.logging.get_logger("optuna").addHandler(logging.StreamHandler(sys.stdout))


def objective(trial: optuna.Trial) -> float:
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2


if __name__ == "__main__":
    tuning_database = tsd.MODEL_TUNING_DB
    study = optuna.create_study(
        study_name="simple_study",
        storage=tuning_database.storage,
        load_if_exists=True,
        direction=optuna.study.StudyDirection.MINIMIZE,
        sampler=None,
        pruner=None
    )
    study.optimize(func=objective, n_trials=3)

