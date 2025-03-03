import argparse
import logging
import sys

import optuna
from optuna.pruners import BasePruner  # add other pruners as needed
from optuna.samplers import BaseSampler  # add other samplers as needed
from optuna.study import StudyDirection
from docktuna.optuna_db.db_instance import get_optuna_db




def objective(trial: optuna.Trial) -> float:
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2


def get_study(
    study_name: str,
    direction: StudyDirection = StudyDirection.MINIMIZE,
    sampler: BaseSampler = None,
    pruner: BasePruner = None,
) ->  optuna.Study:
    optuna_db = get_optuna_db()
    
    return optuna.create_study(
        study_name=study_name,
        storage=optuna_db.storage,
        load_if_exists=True,
        direction=direction,
        sampler=sampler,
        pruner=pruner,
    )


def main(study_name: str = "simple_study", n_trials: int = 3):
    # Add stream handler of stdout to show the messages
    optuna_logger = optuna.logging.get_logger("optuna")
    optuna_logger.addHandler(logging.StreamHandler(sys.stdout))

    study = get_study(study_name=study_name)
    study.optimize(func=objective, n_trials=n_trials)    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run an Optuna study to optimize simple_tune.objective"
    )
    parser.add_argument(
        "--study_name", type=str, default="simple_study", help="Name of the study"
    )
    parser.add_argument(
        "--n_trials", type=int, default=3, help="Number of trials for optimization"
    )
    args = parser.parse_args()
    main(study_name=args.study_name, n_trials=args.n_trials)
