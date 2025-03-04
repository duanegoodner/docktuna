# docktuna

A fully containerized Optuna RDB template

## Description

Docktuna is a template project for running the hyperparameter tuning framework [Optuna](https://github.com/optuna/optuna) with an RDB backend in a fully containerized Docker environment. It includes:
- A Debian-slim-based container for the Python application.
- A PostgreSQL container for storing Optuna studies.

This setup is designed to support scalability, reproducibility, and ease of deployment for hyperparameter tuning experiments.
## Features
- 🐳 Fully Containerized - Everything runs inside Docker.
- 🏗 Pre-configured PostgreSQL - Ready to use with Optuna RDB storage.
- 🔒 Secure Secrets Management - Uses Docker secrets for credentials.
- 🛠 Testing Framework - Includes pytest for automated testing.
- 📦 Poetry Dependency Management - Clean and reproducible environment.
- 🏎 Optimized Performance - Supports NVIDIA GPU acceleration for Optuna trials.


- my_optuna_app
    - Based on a slim Debian image
    - 
- postgres_for_optuna