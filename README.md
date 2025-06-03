# docktuna

A fully containerized Optuna RDB template

## Description

Docktuna is a template project for running the hyperparameter tuning framework [Optuna](https://github.com/optuna/optuna) with an RDB backend in a fully containerized Docker environment. It provides a clean development environment using Conda and Poetry, GPU support, secrets management, and PostgreSQL integration.

## 📚 API Documentation

[View Docktuna API Docs](https://duanegoodner.github.io/docktuna/)

This documentation focuses on the `optuna_db` module and related utilities for managing Optuna studies with a PostgreSQL backend.


## Features
- 🐳 Fully Containerized - Everything runs inside Docker.
- 🏗 Pre-configured PostgreSQL - Ready to use with Optuna RDB storage.
- 🔒 Secure Secrets Management - Uses Docker secrets for credentials.
- 🛠 Testing Framework - Includes pytest for automated testing.
- 📦 Poetry Dependency Management - Clean and reproducible environment.
- 🏎 Optimized Performance - Supports NVIDIA GPU acceleration for Optuna trials.

## Getting Started

### Clone the Repo

```shell
git clone https://github.com/duanegoodner/docktuna
```

### Create Env and Password Files

#### Docker `.env` File

```shell
cp ./docktuna/docker/.env.example ./docktuna/docker/.env
```
Update this line in `.env` to match your local repo path:
```
LOCAL_PROJECT_ROOT=/absolute/path/to/docktuna
```
Replace `/absolute/path/to/docktuna` with your local path to the `docktuna` repo.


#### Docker Secrets Directory
Create password files inside the secrets folder:

```
mkdir -p ./docktuna/docker/secrets

# Example passwords (you choose actual values)
echo "your_postgres_password" > ./docktuna/docker/secrets/optuna_db_postgres_password.txt
echo "your_optuna_user_password" > ./docktuna/docker/secrets/optuna_db_user_password.txt
```

File permissions must allow the Docker daemon to read them (often requires group-readable, e.g., `chmod 640`).



### Build the `optuna_app` Image

```
cd docktuna/docker/docktuna
UID=${UID} GID=${GID} docker compose build
```
Expected output includes:
```
✔ optuna_app  Built
```

### Launch Services
```
UID=${UID} GID=${GID} docker compose up -d
```
Expected Output:
```
[+]
 Running 4/4
 ✔ Network docktuna_default                  Created                         0.2s 
 ✔ Volume "docktuna_optuna_postgres_volume"  Created                         0.0s 
 ✔ Container postgres_for_optuna             Started                         0.5s 
 ✔ Container optuna_app                      Started                         0.6s 
```

### Enter the App Container

```
docker exec -it optuna_app /bin/zsh
```
This opens a shell inside the container at `/home/gen_user/project`, which is mapped to your host repo root.


### Install Python Package in Poetry Environment

```
poetry install
```
Expected output:

```
Installing dependencies from lock file
No dependencies to install or update
Installing the current project: docktuna (0.1.0)
```

### Run Tests

```
poetry run pytest
```
Expected Output:
```
====================== test session starts =================
platform linux -- Python 3.13.3, pytest-8.3.5, pluggy-1.5.0
rootdir: /home/gen_user/project
configfile: pyproject.toml
plugins: anyio-4.9.0, cov-6.0.0
collected 19 items                                                                                                                               

test/test_db_instance.py ...                                                                                                               [ 15%]
test/test_optuna_db.py ............                                                                                                        [ 78%]
test/test_tuning_scripts.py ....                                                                                                           [100%]

---------- coverage: platform linux, python 3.13.3-final-0 -----------
Name                                    Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------------
src/docktuna/__init__.py                    0      0      0      0   100%
src/docktuna/gpu_tune.py                   62      0      6      1    99%
src/docktuna/optuna_db/__init__.py          0      0      0      0   100%
src/docktuna/optuna_db/db_instance.py      16      0      2      0   100%
src/docktuna/optuna_db/optuna_db.py        73      0      2      0   100%
src/docktuna/simple_tune.py                25      0      2      0   100%
-------------------------------------------------------------------------
TOTAL                                     176      0     12      1    99%
Coverage XML written to file coverage.xml
=========================== 19 passed in 9.71s =============================
```
### Check Database Connectivity

```
poetry run python test/check_connections.py
```
Expected output:
```
Successfully checked for existing studies in:
	Database model_tuning on host postgres_for_optuna as user tuner.
	Number of studies found = 4
```

### Run Example Studies


```shell
poetry run python src/docktuna/simple_tune.py
poetry run python src/docktuna/gpu_tune.py
```

## Customizing for a a New Project

When adapting this template for your own tuning experiments:

### 1. Add/Update Dependencies

- Edit pyproject.toml to add or remove Poetry-managed packages
- If needed, update `environment.yml` to add Conda-managed dependencies (e.g., `cudatoolkit`, etc.)


### 2. Define Your Optuna Studies

- Use `src/docktuna/simple_tune.py` or `gpu_tune.py` as templates for your tuning logic.
- Refer to the [API documentation](https://duanegoodner.github.io/docktuna/) for details on `optuna_db` utilities to manage connections and studies.


### 3. Rebuild the Image

After updating dependencies and/or Python code:

```
cd docker/docktuna
UID=$(id -u) GID=$(id -g) docker compose build
```

### 4. Restart the Containers
```
UID=$(id -u) GID=$(id -g) docker compose up -d --force-recreate
```

### Installing Additional Conda Packages

If a package is better managed by Conda instead of Poetry (e.g. `opencv`), you can:
1. Add it to `environment.yml` under `dependencies`:
```
- opencv
```
2. Then rebuild
```
UID=$(id -u) GID=$(id -g) docker compose build
```
This ensures the package gets installed during image build into the Conda environment that Poetry also uses.


## Final Notes

- All development happens inside the optuna_app container.

- PostgreSQL is initialized with Optuna-ready schema using Docker entrypoint scripts.

- No need to install anything locally besides Docker and NVIDIA support (if using GPU).

- Secrets are stored locally (in `./docker/secrets`) and are **not version controlled**.


Happy tuning 🎯






