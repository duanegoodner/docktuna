"""
Example template for running an Optuna study with RDB storage.

This file serves as a **starting point** for users of this project template 
who need to build an application with more complex hyperparameter tuning. 
Modify and expand this template to fit your specific optimization needs.

Usage:
    python example_tuning_template.py --study_name my_study --n_trials 10
"""

import argparse
import logging
import sys

import optuna
from optuna.pruners import BasePruner  # Add other pruners as needed
from optuna.samplers import BaseSampler  # Add other samplers as needed
from optuna.study import StudyDirection

from docktuna.optuna_db.db_instance import get_optuna_db


def objective(trial: optuna.Trial) -> float:
    """
    Defines the objective function for optimization.

    This example function optimizes a simple quadratic function: (x - 2)^2.
    Modify this function to implement your custom tuning objective.

    Args:
        trial: An Optuna trial object that suggests hyperparameters.

    Returns:
        The loss value to be minimized.
    """
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2


def get_study(
    study_name: str,
    direction: StudyDirection = StudyDirection.MINIMIZE,
    sampler: BaseSampler = None,
    pruner: BasePruner = None,
) -> optuna.Study:
    """
    Retrieves or creates an Optuna study using RDB storage.

    Args:
        study_name: The name of the study.
        direction: The optimization direction (MINIMIZE or MAXIMIZE).
        sampler: An optional Optuna sampler for customized search strategies.
        pruner: An optional Optuna pruner for early stopping.

    Returns:
        The Optuna study object.
    """
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
    """
    Runs an Optuna study with the specified parameters.

    Configures logging, retrieves the study, and starts the optimization process.

    Args:
        study_name: The name of the study to create or load.
        n_trials: The number of trials to run in the study.
    """
    # Configure Optuna logging to display messages in the console
    optuna_logger = optuna.logging.get_logger("optuna")
    optuna_logger.addHandler(logging.StreamHandler(sys.stdout))

    study = get_study(study_name=study_name)
    study.optimize(func=objective, n_trials=n_trials)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run an Optuna study to optimize a simple objective function."
    )
    parser.add_argument(
        "--study_name",
        type=str,
        default="simple_study",
        help="Name of the study",
    )
    parser.add_argument(
        "--n_trials",
        type=int,
        default=3,
        help="Number of trials for optimization",
    )
    args = parser.parse_args()
    main(study_name=args.study_name, n_trials=args.n_trials)
