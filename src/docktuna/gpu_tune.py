"""
GPU-accelerated hyperparameter tuning with Optuna.

This script optimizes a simple PyTorch model using RDB storage in Optuna.
If an NVIDIA GPU is available, computations run on CUDA; otherwise, the script falls back to CPU.

Usage:
    python gpu_tune.py --study_name my_study --n_trials 10
"""

import argparse
import logging
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import optuna
from optuna.study import StudyDirection
from docktuna.optuna_db.db_instance import get_optuna_db


# Detect GPU availability and set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Ensure reproducibility
def set_seed(seed: int = 42):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


set_seed()


class SimpleNet(nn.Module):
    """A simple neural network with one hidden layer."""

    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


def generate_synthetic_data(n_samples: int = 1000, input_size: int = 10):
    """Generates synthetic dataset."""
    X = torch.randn(n_samples, input_size, device=device)  # Place on correct device
    y = torch.randn(n_samples, 1, device=device)
    return X, y


def objective(trial: optuna.Trial) -> float:
    """Defines the Optuna objective function for tuning."""
    input_size = 10
    output_size = 1
    hidden_size = trial.suggest_int("hidden_size", 8, 128)

    model = SimpleNet(input_size, hidden_size, output_size).to(device)

    optimizer_name = trial.suggest_categorical("optimizer", ["Adam", "SGD"])
    lr = trial.suggest_loguniform("lr", 1e-5, 1e-1)
    optimizer = getattr(optim, optimizer_name)(model.parameters(), lr=lr)

    loss_fn = nn.MSELoss()
    X, y = generate_synthetic_data()

    for epoch in range(20):
        optimizer.zero_grad()
        predictions = model(X)
        loss = loss_fn(predictions, y)
        loss.backward()
        optimizer.step()

    return loss.item()


def get_study(study_name: str) -> optuna.Study:
    """Retrieves or creates an Optuna study using RDB storage."""
    optuna_db = get_optuna_db()
    return optuna.create_study(
        study_name=study_name,
        storage=optuna_db.storage,
        load_if_exists=True,
        direction=StudyDirection.MINIMIZE,
    )


def main(study_name: str = "gpu_study", n_trials: int = 10):
    """Runs an Optuna study with GPU support (or CPU fallback)."""
    # Configure logging
    optuna_logger = optuna.logging.get_logger("optuna")
    optuna_logger.addHandler(logging.StreamHandler(sys.stdout))

    study = get_study(study_name)
    study.optimize(func=objective, n_trials=n_trials)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GPU-based Optuna tuning.")
    parser.add_argument("--study_name", type=str, default="gpu_study", help="Name of the study")
    parser.add_argument("--n_trials", type=int, default=10, help="Number of trials for optimization")
    args = parser.parse_args()
    main(study_name=args.study_name, n_trials=args.n_trials)
