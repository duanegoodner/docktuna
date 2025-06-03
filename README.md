# Docktuna

A fully containerized template for running Optuna with PostgreSQL-backed RDB storage — powered by Docker, Conda, and Poetry.


[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![PostgreSQL - RDB](https://img.shields.io/badge/PostgreSQL-RDB-blue?logo=postgresql)](https://www.postgresql.org/)
[![Optuna - Hyperparameter Tuning](https://img.shields.io/badge/Optuna-Hyperparameter--Tuning-orange)](https://optuna.org)
[![Conda Environment](https://img.shields.io/badge/Conda-Environment-green?logo=anaconda)](https://docs.conda.io/)
[![Poetry - Dependency Manager](https://img.shields.io/badge/Poetry-Dependency--Manager-blueviolet?logo=python)](https://python-poetry.org/)
[![API Docs](https://img.shields.io/badge/API-Docs-blue?logo=github)](https://duanegoodner.github.io/docktuna/)
[![License](https://img.shields.io/github/license/duanegoodner/docktuna)](LICENSE)






## 📖 Description

Docktuna is a template project for running the hyperparameter tuning framework [Optuna](https://github.com/optuna/optuna) with an RDB backend in a fully containerized Docker environment.  It provides a clean and reproducible Python development environment using Conda and Poetry, with support for GPU-accelerated Optuna trials.

The setup includes a pre-configured PostgreSQL database for Optuna RDB storage, Docker secrets for secure credential management, and entrypoint scripts that automatically initialize the database. The project also includes a testing framework powered by `pytest`, and is designed to require no local Python or PostgreSQL installation — just Docker (and NVIDIA support if using GPUs).

## 📚 API Documentation

The Docktuna API documentation is available at: [Docktuna API Docs](https://duanegoodner.github.io/docktuna/). This documentation focuses on the `optuna_db` module and related utilities for managing Optuna studies with a PostgreSQL backend.

> [!NOTE]
> For general project documentation, just keep reading this README — that’s where everything else lives for now.


## 🚀 Getting Started

### 🧰 Requirements
- Docker
- Optional: Nvidia GPU with drivers supporting CUDA 12.2+ (older versions will likely work but have not been tested)
- Optional: [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

### 🔄 Clone the Repo

```shell
git clone https://github.com/duanegoodner/docktuna
```

### ⚙️ Create Environment and Password Files

#### Docker `.env` File

```shell
cp ./docktuna/docker/.env.example ./docktuna/docker/.env
```
Update this line in `.env` to match your local repo path:
```
LOCAL_PROJECT_ROOT=/absolute/path/to/docktuna
```
Replace `/absolute/path/to/docktuna` with the absolute path to your local `docktuna` repo.


#### Docker Secrets Directory
Create password files inside the secrets folder:

```
mkdir -p ./docktuna/docker/secrets

# Use your own secure passwords here
echo "your_postgres_password" > ./docktuna/docker/secrets/optuna_db_postgres_password.txt
echo "your_optuna_user_password" > ./docktuna/docker/secrets/optuna_db_user_password.txt
```

File permissions must allow the Docker daemon to read them (often requires group-readable, e.g., `chmod 640`).



### 🛠 Build the `optuna_app` Image

```
cd docktuna/docker/docktuna
UID=${UID} GID=${GID} docker compose build
```
Expected output includes:
```
✔ optuna_app  Built
```

### ▶️ Launch Services
To start all services (PostgreSQL + app container):
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

### 🖥 Enter the App Container

```
docker exec -it optuna_app /bin/zsh
```
You’ll land in `/home/gen_user/project`, which maps to your local repo root.

### 📦 Install Python Package in Poetry Environment

```
poetry install
```
Expected output:

```
Installing dependencies from lock file
No dependencies to install or update
Installing the current project: docktuna (0.1.0)
```

### 🧪 Run Tests

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
### 🛢️ Check Database Connectivity

```
poetry run python test/check_connections.py
```
Expected output:
```
Successfully checked for existing Optuna studies in:
	Database model_tuning on host postgres_for_optuna as user tuner.
	Number of studies found = 4
```

### 🎯 Run Example Studies


```shell
poetry run python src/docktuna/simple_tune.py
poetry run python src/docktuna/gpu_tune.py
```

## 🚦 Optional: GPU Support
Docktuna supports NVIDIA GPU acceleration. To enable it, use the override file:
```
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```
Then drop into a container shell as usual with:
```
docker exec -it optuna_app /bin/zsh
```
You can then confirm GPU access by running:
```
nvidia-smi
```
The output should be similar to:
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 575.51.03              Driver Version: 575.51.03      CUDA Version: 12.9     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 3060        On  |   00000000:01:00.0 Off |                  N/A |
|  0%   32C    P8             15W /  170W |      15MiB /  12288MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
                                                                                         
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A         1866637      G   /usr/lib/xorg/Xorg                        4MiB |
+-----------------------------------------------------------------------------------------+
```

If the `nvidia-smi` command fails, ensure:

- NVIDIA drivers are installed
- NVIDIA Container Toolkit is installed

To run without GPU support, just use:
```
docker compose up -d
```

## 🧩 Customizing for a New Project

When adapting this template for your own tuning experiments:

### 1️⃣ Add/Update Dependencies

- Edit `pyproject.toml` to add or remove Poetry-managed packages.
- If needed, update `environment.yml` to add Conda-managed dependencies (e.g., `cudatoolkit`, etc.).


### 2️⃣ Define Your Optuna Studies

- Use `src/docktuna/simple_tune.py` or `gpu_tune.py` as starting points for your tuning logic.
- Refer to the [API docs](https://duanegoodner.github.io/docktuna/) for details on `optuna_db` utilities to manage connections and studies.


### 3️⃣ Rebuild the Image

After updating dependencies and/or Python code:

```
cd docker/docktuna
UID=$(id -u) GID=$(id -g) docker compose build
```

### 4️⃣ Restart the Containers
```
UID=$(id -u) GID=$(id -g) docker compose up -d --force-recreate
```

### ➕ Installing Additional Conda Packages

If you need Conda-specific packages (e.g. `opencv`):
1. Add it to `environment.yml` under `dependencies`:
```yaml
dependencies:
	- opencv
```
2. Rebuild the image
```
UID=$(id -u) GID=$(id -g) docker compose build
```
This ensures the package gets installed during image build into the Conda environment that Poetry also uses.

## 💾 Managing the PostgreSQL Database Volume
The PostgreSQL data is stored in a Docker-managed volume. To inspect:
```
docker volume ls
```
You should see something like:
```
DRIVER    VOLUME NAME
local     docker_optuna_postgres_volume
```
To delete the database (e.g. to start from a clean slate):
```
docker volume rm docker_optuna_postgres_volume
```
This removes all stored data. A fresh database will be created automatically next time you launch the containers using `docker compose up`.


## 🤝 Contributing

Pull requests are welcome! If you find a bug or want to suggest improvements, feel free to open an issue or PR.



## 📝 Final Notes

- 💻 All development occurs inside the `optuna_app` container.
- 🧩 PostgreSQL is initialized via Docker entrypoint scripts.
- 🔐 Secrets in `docker/secrets/` are never committed to version control.
- 🐳 Only Docker (and optional NVIDIA GPU drivers) must be installed locally.



Happy tuning 🎯



