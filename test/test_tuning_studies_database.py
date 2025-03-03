import docktuna.tuning_db.tuning_studies_database as tsd





def test_get_db_dotenv_info():
    model_tuning_db_info = tsd.get_db_dotenv_info(db_name_var="MODEL_TUNING_DB_NAME")


def test_instantiate_db():
    model_tuning_db_info = tsd.get_db_dotenv_info(db_name_var="MODEL_TUNING_DB_NAME")
    db_for_test = tsd.OptunaDatabase(**model_tuning_db_info)

def test_existing_db_name():
    name = tsd.MODEL_TUNING_DB.db_name


def test_existing_db_storage():
    storage = tsd.MODEL_TUNING_DB.storage

def test_existing_db_study_summaries():
    study_summaries = tsd.MODEL_TUNING_DB.study_summaries


