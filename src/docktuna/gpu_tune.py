"""
Hyperparameter tuning using Optuna and PyTorch on GPU.

This script demonstrates how to use Optuna to tune the batch size
and learning rate for a simple neural network trained on synthetic data.

The goal is to **minimize validation loss**.

Usage:
    poetry run python gpu_tune.py --study_name gpu_tuning_study --n_trials 10
"""

import argparse
import logging
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import optuna
import numpy as np
from optuna.study import StudyDirection
from docktuna.optuna_db.db_instance import get_optuna_db

# Set a fixed random seed for reproducibility
SEED = 42
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
np.random.seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False


# Define a simple feedforward neural network
class SimpleNN(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


# Generate fixed synthetic dataset
def generate_synthetic_data(num_samples=1000, input_size=10):
    X = np.random.randn(num_samples, input_size).astype(np.float32)  # Features
    y = np.random.randn(num_samples, 1).astype(np.float32)  # Labels
    return X, y


# Define the objective function for Optuna
def objective(trial: optuna.Trial) -> float:
    """
    Objective function for tuning hyperparameters.

    Args:
        trial (optuna.Trial): A trial object to suggest hyperparameters.

    Returns:
        float: Validation loss (lower is better).
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Sample hyperparameters
    hidden_size = trial.suggest_int("hidden_size", 16, 256, step=16)
    batch_size = trial.suggest_categorical("batch_size", [16, 32, 64, 128])
    learning_rate = trial.suggest_loguniform("learning_rate", 1e-4, 1e-2)

    # Load fixed synthetic dataset
    X, y = generate_synthetic_data()
    dataset = torch.utils.data.TensorDataset(
        torch.tensor(X), torch.tensor(y)
    )
    train_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model, loss function, and optimizer
    model = SimpleNN(input_size=10, hidden_size=hidden_size, output_size=1).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Training loop (1 epoch for quick tuning)
    model.train()
    for batch_x, batch_y in train_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)

        optimizer.zero_grad()
        predictions = model(batch_x)
        loss = criterion(predictions, batch_y)
        loss.backward()
        optimizer.step()

    # Return final loss (as objective metric)
    return loss.item()


def get_study(study_name: str) -> optuna.Study:
    """
    Retrieves or creates an Optuna study using RDB storage.

    Args:
        study_name (str): The name of the study.

    Returns:
        optuna.Study: The study object.
    """
    optuna_db = get_optuna_db()
    return optuna.create_study(
        study_name=study_name,
        storage=optuna_db.storage,
        load_if_exists=True,
        direction=StudyDirection.MINIMIZE,  # Minimizing loss
    )


def main(study_name: str = "gpu_tuning_study", n_trials: int = 10):
    """
    Runs an Optuna study for tuning the neural network hyperparameters.

    Args:
        study_name (str): The name of the Optuna study.
        n_trials (int): Number of trials to run.
    """
    # Configure Optuna logging
    optuna_logger = optuna.logging.get_logger("optuna")
    optuna_logger.addHandler(logging.StreamHandler(sys.stdout))

    study = get_study(study_name=study_name)
    study.optimize(objective, n_trials=n_trials)

    # Print best parameters
    print("Best hyperparameters:", study.best_params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hyperparameter tuning using Optuna and PyTorch on GPU."
    )
    parser.add_argument("--study_name", type=str, default="gpu_tuning_study", help="Name of the study")
    parser.add_argument("--n_trials", type=int, default=10, help="Number of trials for optimization")
    args = parser.parse_args()

    main(study_name=args.study_name, n_trials=args.n_trials)
