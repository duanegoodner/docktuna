#!/bin/bash

set -e
set -u

function create_user() {
	local new_user=$1
	local password_file=$2

	echo "  Creating user '$new_user'"
	password=$(cat "$password_file")
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE USER $new_user WITH PASSWORD '$password';
EOSQL
}

function create_database() {
	local new_database=$1
	echo "  Creating user and database '$new_database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE DATABASE $new_database;
EOSQL
}

function grant_privileges() {
  local database=$1
  local user=$2
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$database" <<-EOSQL
	    ALTER USER $user SET search_path = public;
	    GRANT USAGE ON SCHEMA public TO $user;
	    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $user;
	    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $user;
	    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO $user;
	    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON TYPES TO $user;
	    GRANT CREATE ON SCHEMA public TO $user;
EOSQL

}

create_user "$OPTUNA_DB_USER" "$OPTUNA_DB_PASSWORD_FILE"
create_database "$OPTUNA_DB_NAME"
grant_privileges "$OPTUNA_DB_NAME" "$OPTUNA_DB_USER"

