from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from data_processing.read_data import fetch_recent_signals


def test_fetch_recent_signals_raises_error_when_limit_is_invalid():
    with pytest.raises(ValueError) as error:
        fetch_recent_signals(0)

    assert "limit" in str(error.value)


@patch("data_processing.read_data._get_db_connection")
def test_fetch_recent_signals_returns_expected_format(mock_get_db_connection):
    fake_connection = Mock()
    fake_cursor = Mock()
    fake_connection.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = [
        (datetime(2026, 4, 22, 8, 15, 0), "sensor_001", 52.1, 25.2, 60.5, "simulation"),
        (datetime(2026, 4, 22, 8, 0, 0), "sensor_001", 50.1, 25.0, 61.0, "simulation"),
    ]
    mock_get_db_connection.return_value = fake_connection

    result = fetch_recent_signals(limit=2)

    assert len(result) == 2
    assert result[0]["signal_timestamp"] == datetime(2026, 4, 22, 8, 0, 0)
    assert result[0]["sensor_id"] == "sensor_001"
    assert result[0]["signal_value"] == 50.1
    assert result[0]["source"] == "simulation"
    fake_cursor.execute.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_connection.close.assert_called_once()


@patch("data_processing.read_data._get_db_connection")
def test_fetch_recent_signals_applies_sensor_filter(mock_get_db_connection):
    fake_connection = Mock()
    fake_cursor = Mock()
    fake_connection.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = []
    mock_get_db_connection.return_value = fake_connection

    fetch_recent_signals(limit=5, sensor_id="sensor_abc")

    query, params = fake_cursor.execute.call_args.args
    assert "WHERE sensor_id = %s" in query
    assert params == ("sensor_abc", 5)
