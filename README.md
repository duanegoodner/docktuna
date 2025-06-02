# docktuna

A fully containerized Optuna RDB template

## Description

Docktuna is a template project for running the hyperparameter tuning framework [Optuna](https://github.com/optuna/optuna) with an RDB backend in a fully containerized Docker environment. 

## Features
- 🐳 Fully Containerized - Everything runs inside Docker.
- 🏗 Pre-configured PostgreSQL - Ready to use with Optuna RDB storage.
- 🔒 Secure Secrets Management - Uses Docker secrets for credentials.
- 🛠 Testing Framework - Includes pytest for automated testing.
- 📦 Poetry Dependency Management - Clean and reproducible environment.
- 🏎 Optimized Performance - Supports NVIDIA GPU acceleration for Optuna trials.

## Getting Started



### Build the `optuna_app` Image

```
git clone https://github.com/duanegoodner/docktuna
cd docktuna/docker/docktuna
UID=${UID} GID=${GID} docker compose build
```
Output should include:
```
✔ optuna_app  Built
```
Key things to note about the `optuna_app` image:
- Based on a Debian Slim image
- Contains a **sudo-privileged non-root user**, `gen_user` with `UID` and `GID` values that match the `UID` and `GID` of the local user building the image.
- Poetry and Miniconda are installed under the `gen_user` home directory/

### Use `docker compose` to Start Containers
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
 ✔ Container optuna_app                   Started                         0.6s 
```
The `optuna_app` container is based on our image of the same name. `postgres_for_optuna` is based on a PostgreSQL image and has Docker volume `docktuna_optuna_postgres_volume` mapped to its storage.

### Enter `optuna_app` Container

```
docker exec -it optuna_app /bin/zsh
```
This will take you a `zsh` prompt in working directory `/home/gen_user/project/` inside the `optuna_app` container. This container path is mapped to the local project root, so the output of `ls` should match the contents of your local repo root director:
```
LICENSE  README.md  coverage.xml  docker  environment.yml  poetry.lock  pyproject.toml  src  test
```

## Use a Poetry Environment


```
poetry install
```
```
poetry run pytest
```
Expected Output:
```
platform linux -- Python 3.12.9, pytest-8.3.5, pluggy-1.5.0
rootdir: /home/gen_user/project
configfile: pyproject.toml
plugins: cov-6.0.0
collected 19 items                                                                                                                               

test/test_db_instance.py ...                                                                                                               [ 15%]
test/test_optuna_db.py ............                                                                                                        [ 78%]
test/test_tuning_scripts.py ....                                                                                                           [100%]

---------- coverage: platform linux, python 3.12.9-final-0 -----------
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

=========================================== 19 passed in 11.61s ===========================================
```


```
poetry run python test/check_connections.py
Successfully checked for existing studies in:
	Database model_tuning on host postgres_for_optuna as user tuner.
	Number of studies found = 4
```

## Use a Conda Environment

```
conda env create -f environment.yml
conda activate docktuna
pip install .
```

```
pytest
```