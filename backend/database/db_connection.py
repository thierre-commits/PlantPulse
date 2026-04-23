import os
from typing import Optional

import psycopg2
from psycopg2 import OperationalError
from psycopg2.extensions import connection as PGConnection


def _get_required_env_var(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Variavel de ambiente obrigatoria ausente para conexao com o PostgreSQL: {name}"
        )

    return value


def _get_db_port() -> int:
    raw_port = _get_required_env_var("DB_PORT")

    try:
        port = int(raw_port)
    except ValueError as error:
        raise ValueError(
            "A variavel DB_PORT deve ser um numero inteiro valido."
        ) from error

    if port <= 0 or port > 65535:
        raise ValueError(
            "A variavel DB_PORT deve estar entre 1 e 65535."
        )

    return port


def get_db_connection() -> PGConnection:
    db_host = _get_required_env_var("DB_HOST")
    db_port = _get_db_port()
    db_name = _get_required_env_var("DB_NAME")
    db_user = _get_required_env_var("DB_USER")
    db_password = _get_required_env_var("DB_PASSWORD")

    try:
        return psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
        )
    except OperationalError as error:
        raise ConnectionError(
            "Nao foi possivel conectar ao PostgreSQL. Verifique as credenciais, "
            "se o banco existe e se o servidor esta acessivel."
        ) from error


def close_connection(connection: Optional[PGConnection]) -> None:
    if connection is not None and not connection.closed:
        connection.close()
