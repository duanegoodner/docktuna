import datetime
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote

import optuna
from optuna.storages import RDBStorage


@contextmanager
def temporary_optuna_verbosity(logging_level: int):
    original_verbosity = optuna.logging.get_verbosity()
    optuna.logging.set_verbosity(logging_level)
    try:
        yield
    finally:
        optuna.logging.set_verbosity(original_verbosity)


class OptunaDatabase:
    def __init__(
        self,
        username_secret: str,
        db_password_secret: str,
        db_name_secret: str,
        hostname_secret: str,
    ):
        self._username_secret = username_secret
        self._db_password_secret = db_password_secret
        self._db_name_secret = db_name_secret
        self._hostname_secret = hostname_secret
    
    def _read_secret(self, secret_name: str) -> str:
        secret_path = Path("/run/secrets") / secret_name
        try:
            with secret_path.open(mode="r") as f:
                file_content = f.read()
                return file_content.strip()
        except FileNotFoundError:
            raise Exception(f"Secret {secret_name} not found!")
    
    @property
    def username(self) -> str:
        return self._read_secret(self._username_secret)
    
    @property
    def db_name(self) -> str:
        return self._read_secret(self._db_name_secret)

    @property
    def hostname(self) -> str:
        return self._read_secret(self._hostname_secret)

    @property
    def _db_url(self) -> str:
        """Constructs the database URL dynamically without storing the password."""
        user = self._read_secret(self._username_secret)
        password = self._read_secret(self._db_password_secret)
        db_name = self._read_secret(self._db_name_secret)
        host = self._read_secret(self._hostname_secret)

        return (
            f"postgresql+psycopg2://{user}:{quote(password, safe='')}@{host}/{db_name}"
        )

    @property
    def storage(self) -> RDBStorage:
        """Returns an Optuna storage object using the connection pool."""
        return RDBStorage(url=self._db_url)

    @property
    def study_summaries(self) -> list[optuna.study.StudySummary]:
        return optuna.study.get_all_study_summaries(storage=self.storage)

    def is_in_db(self, study_name: str) -> bool:
        return study_name in {summary.study_name for summary in self.study_summaries}

    def get_study_summary(self, study_name: str) -> optuna.study.StudySummary:
        return next(
            summary
            for summary in self.study_summaries
            if summary.study_name == study_name
        )

    def get_best_params(self, study_name: str) -> dict[str, any]:
        study_summary = self.get_study_summary(study_name=study_name)
        if study_summary is None or study_summary.best_trial is None:
            return {}
        return study_summary.best_trial.params

    def get_study(self, study_name: str) -> optuna.Study:
        with temporary_optuna_verbosity(logging_level=optuna.logging.WARNING):
            return optuna.create_study(
                study_name=study_name, storage=self.storage, load_if_exists=True
            )

    def get_all_studies(self) -> list[optuna.Study]:
        with temporary_optuna_verbosity(logging_level=optuna.logging.WARNING):
            return [
                self.get_study(study_name)
                for study_name in {summary.study_name for summary in self.study_summaries}
            ]
    
    @property
    def num_existing_studies(self) -> int:
        all_studies = self.get_all_studies()
        return len(all_studies)

    @staticmethod
    def get_last_update_time(study: optuna.Study) -> datetime.datetime:
        trial_complete_times = [
            trial.datetime_complete for trial in study.trials if trial.datetime_complete
        ]
        return (
            max(trial_complete_times)
            if trial_complete_times
            else datetime.datetime(1, 1, 1)
        )

    def get_latest_study(self) -> optuna.Study:
        sorted_studies = sorted(
            self.get_all_studies(),
            key=lambda x: self.get_last_update_time(x),
            reverse=True,
        )
        return sorted_studies[0] if sorted_studies else None




# MODEL_TUNING_DB = OptunaDatabase(
#     username_secret="tuning_dbs_user",
#     db_password_secret="tuningdb_tuner_password",
#     db_name_secret="model_tuning_db_name",
#     hostname_secret="postgres_dbs_host"
# )

# db_name = MODEL_TUNING_DB.db_name

