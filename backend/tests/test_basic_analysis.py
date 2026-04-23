import pytest

from data_processing.basic_analysis import analyze_signals


def _build_row(signal_value, temperature=20.0, humidity=50.0):
    return {
        "signal_value": signal_value,
        "temperature": temperature,
        "humidity": humidity,
    }


def test_analyze_signals_raises_error_when_data_is_empty():
    with pytest.raises(ValueError) as error:
        analyze_signals([])

    assert "data nao pode ser vazio" in str(error.value)


def test_analyze_signals_returns_basic_metrics():
    data = [
        {
            "signal_timestamp": "2026-04-22 08:00:00",
            "sensor_id": "sensor_001",
            "signal_value": 10.0,
            "temperature": 20.0,
            "humidity": 50.0,
            "source": "simulation",
        },
        {
            "signal_timestamp": "2026-04-22 08:15:00",
            "sensor_id": "sensor_001",
            "signal_value": 20.0,
            "temperature": 22.0,
            "humidity": 60.0,
            "source": "simulation",
        },
    ]

    result = analyze_signals(data)

    assert result["total_records"] == 2
    assert result["signal_mean"] == 15.0
    assert result["signal_min"] == 10.0
    assert result["signal_max"] == 20.0
    assert result["signal_amplitude"] == 10.0
    assert result["temperature_mean"] == 21.0
    assert result["humidity_mean"] == 55.0
    assert result["anomaly_count"] == 0
    assert result["peak_count"] == 0


def test_analyze_signals_detects_rising_trend():
    data = [_build_row(100.0), _build_row(101.0), _build_row(110.0), _build_row(111.0)]

    result = analyze_signals(data)

    assert result["trend"] == "rising"


def test_analyze_signals_detects_falling_trend():
    data = [_build_row(111.0), _build_row(110.0), _build_row(101.0), _build_row(100.0)]

    result = analyze_signals(data)

    assert result["trend"] == "falling"


def test_analyze_signals_detects_stable_trend():
    data = [_build_row(100.0), _build_row(101.0), _build_row(102.0), _build_row(103.0)]

    result = analyze_signals(data)

    assert result["trend"] == "stable"


def test_analyze_signals_uses_dynamic_tolerance_based_on_mean():
    data = [_build_row(200.0), _build_row(201.0), _build_row(207.0), _build_row(208.0)]

    result = analyze_signals(data)

    assert result["trend"] == "stable"


def test_analyze_signals_detects_positive_anomaly():
    data = [
        _build_row(10.0),
        _build_row(10.0),
        _build_row(10.0),
        _build_row(30.0),
    ]

    result = analyze_signals(data)

    assert result["anomaly_count"] == 1
    assert result["peak_count"] == 1


def test_analyze_signals_detects_negative_anomaly():
    data = [
        _build_row(20.0),
        _build_row(20.0),
        _build_row(20.0),
        _build_row(-10.0),
    ]

    result = analyze_signals(data)

    assert result["anomaly_count"] == 1


def test_analyze_signals_classifies_low_variability():
    data = [_build_row(100.0), _build_row(101.0), _build_row(99.0), _build_row(100.5)]

    result = analyze_signals(data)

    assert result["variability"] == "low"


def test_analyze_signals_classifies_medium_variability():
    data = [_build_row(100.0), _build_row(110.0), _build_row(90.0), _build_row(105.0)]

    result = analyze_signals(data)

    assert result["variability"] == "medium"


def test_analyze_signals_classifies_high_variability():
    data = [_build_row(20.0), _build_row(80.0), _build_row(140.0), _build_row(200.0)]

    result = analyze_signals(data)

    assert result["variability"] == "high"


def test_analyze_signals_returns_non_empty_summary():
    data = [_build_row(10.0), _build_row(12.0)]

    result = analyze_signals(data)

    assert result["summary"].strip() != ""
    assert "tendencia" in result["summary"]
    assert "variabilidade" in result["summary"]
    assert "anomalia" in result["summary"]
