from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from data_processing.insert_data import (
    INSERT_BATCH_SIZE,
    INSERT_SIGNALS_QUERY,
    insert_signals,
    load_csv,
)


def _temporary_csv_file(filename: str) -> Path:
    return Path(__file__).resolve().with_name(filename)


def test_load_csv_reads_valid_file():
    csv_file = _temporary_csv_file("_tmp_valid_signals.csv")
    try:
        csv_file.write_text(
            "\n".join(
                [
                    "signal_timestamp,sensor_id,signal_value,temperature,humidity,source",
                    "2026-04-22 08:00:00,sensor_001,50.1,25.0,60.0,simulation",
                    "2026-04-22 08:15:00,sensor_001,51.2,25.4,59.5,simulation",
                ]
            ),
            encoding="utf-8",
        )

        data = load_csv(csv_file)

        assert len(data) == 2
        assert data[0]["sensor_id"] == "sensor_001"
    finally:
        csv_file.unlink(missing_ok=True)


def test_load_csv_raises_error_for_invalid_columns():
    csv_file = _temporary_csv_file("_tmp_invalid_signals.csv")
    try:
        csv_file.write_text(
            "\n".join(
                [
                    "timestamp,sensor_id,signal_value,temperature,humidity,source",
                    "2026-04-22 08:00:00,sensor_001,50.1,25.0,60.0,simulation",
                ]
            ),
            encoding="utf-8",
        )

        with pytest.raises(ValueError) as error:
            load_csv(csv_file)

        assert "CSV invalido" in str(error.value)
    finally:
        csv_file.unlink(missing_ok=True)


@patch("data_processing.insert_data._get_db_connection")
def test_insert_signals_executes_batch_insert(mock_get_db_connection):
    fake_connection = Mock()
    fake_connection.closed = False
    fake_cursor = Mock()
    fake_connection.cursor.return_value = fake_cursor
    mock_get_db_connection.return_value = fake_connection

    data = [
        {
            "signal_timestamp": "2026-04-22 08:00:00",
            "sensor_id": "sensor_001",
            "signal_value": "50.1",
            "temperature": "25.0",
            "humidity": "60.0",
            "source": "simulation",
        },
        {
            "signal_timestamp": "2026-04-22 08:15:00",
            "sensor_id": "sensor_001",
            "signal_value": "51.2",
            "temperature": "25.4",
            "humidity": "59.5",
            "source": "simulation",
        },
    ]

    insert_signals(data)

    fake_cursor.executemany.assert_called_once()
    executed_rows = fake_cursor.executemany.call_args[0][1]
    assert len(executed_rows) == 2
    assert executed_rows[0][1] == "sensor_001"
    fake_connection.commit.assert_called_once()
    fake_connection.rollback.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_connection.close.assert_called_once()


def test_insert_query_ignores_duplicate_sensor_timestamp_pairs():
    assert "ON CONFLICT (sensor_id, signal_timestamp) DO NOTHING" in INSERT_SIGNALS_QUERY


@patch("data_processing.insert_data._get_db_connection")
def test_insert_signals_splits_large_payload_into_multiple_batches(
    mock_get_db_connection,
):
    fake_connection = Mock()
    fake_connection.closed = False
    fake_cursor = Mock()
    fake_connection.cursor.return_value = fake_cursor
    mock_get_db_connection.return_value = fake_connection

    data = [
        {
            "signal_timestamp": f"2026-04-22 08:{index % 60:02d}:00",
            "sensor_id": "sensor_001",
            "signal_value": "50.1",
            "temperature": "25.0",
            "humidity": "60.0",
            "source": "simulation",
        }
        for index in range(INSERT_BATCH_SIZE + 1)
    ]

    insert_signals(data)

    assert fake_cursor.executemany.call_count == 2
    first_batch = fake_cursor.executemany.call_args_list[0].args[1]
    second_batch = fake_cursor.executemany.call_args_list[1].args[1]
    assert len(first_batch) == INSERT_BATCH_SIZE
    assert len(second_batch) == 1
    fake_connection.commit.assert_called_once()


@patch("data_processing.insert_data._get_db_connection")
def test_insert_signals_rolls_back_when_insert_fails(mock_get_db_connection):
    fake_connection = Mock()
    fake_connection.closed = False
    fake_cursor = Mock()
    fake_cursor.executemany.side_effect = Exception("insert failed")
    fake_connection.cursor.return_value = fake_cursor
    mock_get_db_connection.return_value = fake_connection

    data = [
        {
            "signal_timestamp": "2026-04-22 08:00:00",
            "sensor_id": "sensor_001",
            "signal_value": "50.1",
            "temperature": "25.0",
            "humidity": "60.0",
            "source": "simulation",
        }
    ]

    with pytest.raises(RuntimeError) as error:
        insert_signals(data)

    assert "A transacao foi revertida" in str(error.value)
    assert "insert failed" in str(error.value)
    assert error.value.__cause__ is not None
    fake_connection.rollback.assert_called_once()
    fake_connection.commit.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_connection.close.assert_called_once()


@patch("data_processing.insert_data._get_db_connection")
def test_insert_signals_raises_clear_error_on_connection_failure(mock_get_db_connection):
    mock_get_db_connection.side_effect = ConnectionError("database unavailable")

    data = [
        {
            "signal_timestamp": "2026-04-22 08:00:00",
            "sensor_id": "sensor_001",
            "signal_value": "50.1",
            "temperature": "25.0",
            "humidity": "60.0",
            "source": "simulation",
        }
    ]

    with pytest.raises(RuntimeError) as error:
        insert_signals(data)

    assert "Erro ao inserir sinais no PostgreSQL" in str(error.value)
    assert "database unavailable" in str(error.value)
    assert error.value.__cause__ is not None
