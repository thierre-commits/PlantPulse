from unittest.mock import Mock, patch

import pytest
from psycopg2 import OperationalError

from database.db_connection import close_connection, get_db_connection


@patch("database.db_connection.psycopg2.connect")
def test_get_db_connection_returns_connection(mock_connect, monkeypatch):
    fake_connection = Mock()
    mock_connect.return_value = fake_connection

    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "plantpulse")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "postgres")

    connection = get_db_connection()

    assert connection == fake_connection
    mock_connect.assert_called_once_with(
        host="localhost",
        port=5432,
        dbname="plantpulse",
        user="postgres",
        password="postgres",
    )


def test_get_db_connection_raises_error_when_env_is_missing(monkeypatch):
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    with pytest.raises(ValueError) as error:
        get_db_connection()

    assert "DB_HOST" in str(error.value)


def test_get_db_connection_raises_error_when_port_is_invalid(monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "porta-invalida")
    monkeypatch.setenv("DB_NAME", "plantpulse")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "postgres")

    with pytest.raises(ValueError) as error:
        get_db_connection()

    assert "DB_PORT" in str(error.value)


@patch("database.db_connection.psycopg2.connect")
def test_get_db_connection_raises_clear_error_on_operational_failure(
    mock_connect, monkeypatch
):
    mock_connect.side_effect = OperationalError("database unavailable")

    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "plantpulse")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "postgres")

    with pytest.raises(ConnectionError) as error:
        get_db_connection()

    assert "Nao foi possivel conectar ao PostgreSQL" in str(error.value)


def test_close_connection_closes_open_connection():
    fake_connection = Mock()
    fake_connection.closed = False

    close_connection(fake_connection)

    fake_connection.close.assert_called_once()


def test_close_connection_ignores_none():
    close_connection(None)
