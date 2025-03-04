import datetime
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote

import optuna
from optuna.storages import RDBStorage


@contextmanager
def temporary_optuna_verbosity(logging_level: int):
    """
    Temporarily sets Optuna's logging verbosity to the specified level
    and restores the original level after execution.

    Args:
        logging_level: Optuna logging level to temporarily set.
    """
    original_verbosity = optuna.logging.get_verbosity()
    optuna.logging.set_verbosity(logging_level)
    try:
        yield
    finally:
        optuna.logging.set_verbosity(original_verbosity)


class OptunaDatabase:
    """
    Handles database interactions for Optuna studies, including secure
    retrieval of credentials from Docker secrets and connection management.
    """

    def __init__(
        self,
        username: str,
        db_password_secret: str,
        db_name: str,
        hostname: str,
    ):
        """
        Initializes an OptunaDatabase instance with database connection details.

        Args:
            username: Database username.
            db_password_secret: Secret name for the database password.
            db_name: Name of the database.
            hostname: Database host.
        """
        self._username = username
        self._db_password_secret = db_password_secret
        self._db_name = db_name
        self._hostname = hostname

    def _read_secret(self, secret_name: str) -> str:
        """
        Reads a secret value from the Docker secrets directory.

        Args:
            secret_name: The name of the secret file to read.

        Returns:
            The contents of the secret file.

        Raises:
            Exception: If the secret file is not found.
        """
        secret_path = Path("/run/secrets") / secret_name
        try:
            with secret_path.open(mode="r") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise Exception(f"Secret {secret_name} not found!")

    @property
    def username(self) -> str:
        """Retrieves the database username from secrets."""
        return self._username

    @property
    def db_name(self) -> str:
        """Retrieves the database name from secrets."""
        return self._db_name

    @property
    def hostname(self) -> str:
        """Retrieves the database hostname from secrets."""
        return self._hostname

    @property
    def _db_url(self) -> str:
        """
        Constructs a secure database connection URL dynamically
        using credentials stored in Docker secrets.

        Returns:
            The formatted database connection URL.
        """
        user = self._username
        password = self._read_secret(self._db_password_secret)
        db_name = self._db_name
        host = self._hostname

        return f"postgresql+psycopg2://{user}:{quote(password, safe='')}@{host}/{db_name}"

    @property
    def storage(self) -> RDBStorage:
        """
        Creates an Optuna RDBStorage instance for persistent study storage.

        Returns:
            The Optuna storage backend.
        """
        return RDBStorage(url=self._db_url)

    @property
    def study_summaries(self) -> list[optuna.study.StudySummary]:
        """
        Retrieves summaries of all studies stored in the database.

        Returns:
            A list of study summaries.
        """
        return optuna.study.get_all_study_summaries(storage=self.storage)

    def is_in_db(self, study_name: str) -> bool:
        """
        Checks if a study exists in the database.

        Args:
            study_name: The name of the study.

        Returns:
            True if the study exists, False otherwise.
        """
        return study_name in {
            summary.study_name for summary in self.study_summaries
        }

    def get_study_summary(self, study_name: str) -> optuna.study.StudySummary:
        """
        Retrieves the summary of a specific study.

        Args:
            study_name: The name of the study.

        Returns:
            The summary of the study.

        Raises:
            StopIteration: If the study is not found.
        """
        return next(
            summary
            for summary in self.study_summaries
            if summary.study_name == study_name
        )

    def get_best_params(self, study_name: str) -> dict[str, any]:
        """
        Retrieves the best hyperparameters from a completed study.

        Args:
            study_name: The name of the study.

        Returns:
            The best hyperparameters, or an empty dictionary if no trials exist.
        """
        study_summary = self.get_study_summary(study_name=study_name)
        if study_summary is None or study_summary.best_trial is None:
            return {}
        return study_summary.best_trial.params

    def get_study(self, study_name: str) -> optuna.Study:
        """
        Retrieves or creates an Optuna study.

        Args:
            study_name: The name of the study.

        Returns:
            The retrieved or newly created study.
        """
        with temporary_optuna_verbosity(logging_level=optuna.logging.WARNING):
            return optuna.create_study(
                study_name=study_name,
                storage=self.storage,
                load_if_exists=True,
            )

    def get_all_studies(self) -> list[optuna.Study]:
        """
        Retrieves all studies stored in the database.

        Returns:
            A list of all Optuna studies.
        """
        with temporary_optuna_verbosity(logging_level=optuna.logging.WARNING):
            return [
                self.get_study(study_name)
                for study_name in {
                    summary.study_name for summary in self.study_summaries
                }
            ]

    @property
    def num_existing_studies(self) -> int:
        """
        Returns the number of existing studies in the database.

        Returns:
            The total number of studies.
        """
        return len(self.get_all_studies())

    @staticmethod
    def get_last_update_time(study: optuna.Study) -> datetime.datetime:
        """
        Retrieves the last update time of a given study.

        Args:
            study: The study object.

        Returns:
            The timestamp of the most recent trial completion,
            or a default old date if no trials exist.
        """
        trial_complete_times = [
            trial.datetime_complete
            for trial in study.trials
            if trial.datetime_complete
        ]
        return (
            max(trial_complete_times)
            if trial_complete_times
            else datetime.datetime(1, 1, 1)
        )

    def get_latest_study(self) -> optuna.Study:
        """
        Retrieves the most recently updated study.

        Returns:
            The study with the most recent completed trial,
            or None if no studies exist.
        """
        sorted_studies = sorted(
            self.get_all_studies(),
            key=lambda x: self.get_last_update_time(x),
            reverse=True,
        )
        return sorted_studies[0] if sorted_studies else None
