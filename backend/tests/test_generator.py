from datetime import datetime
from pathlib import Path

import pytest

from sensor_simulation.plant_signal_generator import export_to_csv, generate_signals


def test_generate_signals_returns_expected_number_of_points():
    data = generate_signals(
        num_points=10,
        sensor_id="sensor_test",
        start_time=datetime(2026, 4, 22, 8, 0, 0),
        interval_seconds=60,
    )

    assert len(data) == 10


def test_generate_signals_contains_expected_columns():
    data = generate_signals(
        num_points=1,
        sensor_id="sensor_test",
        start_time=datetime(2026, 4, 22, 8, 0, 0),
        interval_seconds=60,
    )

    expected_columns = {
        "signal_timestamp",
        "sensor_id",
        "signal_value",
        "temperature",
        "humidity",
        "source",
    }

    assert set(data[0].keys()) == expected_columns


def test_generate_signals_keeps_values_within_expected_ranges():
    data = generate_signals(
        num_points=100,
        sensor_id="sensor_test",
        start_time=datetime(2026, 4, 22, 8, 0, 0),
        interval_seconds=60,
    )

    for row in data:
        assert 0 <= row["signal_value"] <= 100
        assert 15 <= row["temperature"] <= 35
        assert 30 <= row["humidity"] <= 90
        assert row["sensor_id"] == "sensor_test"
        assert row["source"] == "simulation"


def test_generate_signals_is_reproducible_with_fixed_seed():
    start_time = datetime(2026, 4, 22, 8, 0, 0)

    first_run = generate_signals(
        num_points=5,
        sensor_id="sensor_test",
        start_time=start_time,
        interval_seconds=60,
        seed=123,
    )
    second_run = generate_signals(
        num_points=5,
        sensor_id="sensor_test",
        start_time=start_time,
        interval_seconds=60,
        seed=123,
    )

    assert first_run == second_run


def test_generate_signals_changes_output_with_different_seeds():
    start_time = datetime(2026, 4, 22, 8, 0, 0)

    first_run = generate_signals(
        num_points=5,
        sensor_id="sensor_test",
        start_time=start_time,
        interval_seconds=60,
        seed=123,
    )
    second_run = generate_signals(
        num_points=5,
        sensor_id="sensor_test",
        start_time=start_time,
        interval_seconds=60,
        seed=456,
    )

    assert first_run != second_run


@pytest.mark.parametrize(
    ("num_points", "sensor_id", "interval_seconds", "expected_message"),
    [
        (0, "sensor_test", 60, "num_points"),
        (10, "sensor_test", 0, "interval_seconds"),
        (10, "", 60, "sensor_id"),
    ],
)
def test_generate_signals_rejects_invalid_inputs(
    num_points, sensor_id, interval_seconds, expected_message
):
    with pytest.raises(ValueError) as error:
        generate_signals(
            num_points=num_points,
            sensor_id=sensor_id,
            start_time=datetime(2026, 4, 22, 8, 0, 0),
            interval_seconds=interval_seconds,
        )

    assert expected_message in str(error.value)


def test_export_to_csv_rejects_invalid_structure(tmp_path):
    output_file = tmp_path / "invalid.csv"
    invalid_data = [
        {
            "signal_timestamp": "2026-04-22 08:00:00",
            "sensor_id": "sensor_test",
            "signal_value": 50.0,
            "temperature": 25.0,
            "humidity": 60.0,
        }
    ]

    with pytest.raises(ValueError) as error:
        export_to_csv(invalid_data, output_file)

    assert "Estrutura invalida em data" in str(error.value)


def test_export_to_csv_rejects_invalid_types(tmp_path):
    output_file = tmp_path / "invalid_types.csv"
    invalid_data = [
        {
            "signal_timestamp": "",
            "sensor_id": "sensor_test",
            "signal_value": "50.0",
            "temperature": 25.0,
            "humidity": 60.0,
            "source": "simulation",
        }
    ]

    with pytest.raises(ValueError) as error:
        export_to_csv(invalid_data, output_file)

    assert "Tipo invalido em data" in str(error.value)
    assert "indice 0" in str(error.value)


def test_export_to_csv_creates_file_with_expected_header_and_line_count(tmp_path):
    output_file = tmp_path / "nested" / "signals.csv"
    data = generate_signals(
        num_points=2,
        sensor_id="sensor_test",
        start_time=datetime(2026, 4, 22, 8, 0, 0),
        interval_seconds=60,
        seed=7,
    )

    export_to_csv(data, output_file)

    file_content = Path(output_file).read_text(encoding="utf-8").splitlines()

    assert output_file.exists()
    assert (
        file_content[0]
        == "signal_timestamp,sensor_id,signal_value,temperature,humidity,source"
    )
    assert len(file_content) == 3
