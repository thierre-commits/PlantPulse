from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@patch("app.routes.signals.fetch_recent_signals")
def test_signals_endpoint_returns_data(mock_fetch_recent_signals):
    mock_fetch_recent_signals.return_value = [
        {
            "signal_timestamp": "2026-04-22 08:00:00",
            "sensor_id": "sensor_001",
            "signal_value": 50.1,
            "temperature": 25.0,
            "humidity": 60.0,
            "source": "simulation",
        }
    ]

    response = client.get("/api/v1/signals", params={"limit": 1})

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "message" in response.json()
    assert isinstance(response.json()["data"], list)
    assert response.json()["data"][0]["sensor_id"] == "sensor_001"


@patch("app.routes.analysis.analyze_signals")
@patch("app.routes.analysis.fetch_recent_signals")
def test_analysis_endpoint_returns_analysis(
    mock_fetch_recent_signals, mock_analyze_signals
):
    mock_fetch_recent_signals.return_value = [
        {
            "signal_timestamp": "2026-04-22 08:00:00",
            "sensor_id": "sensor_001",
            "signal_value": 50.1,
            "temperature": 25.0,
            "humidity": 60.0,
            "source": "simulation",
        }
    ]
    mock_analyze_signals.return_value = {
        "total_records": 1,
        "signal_mean": 50.1,
        "signal_min": 50.1,
        "signal_max": 50.1,
        "signal_amplitude": 0.0,
        "temperature_mean": 25.0,
        "humidity_mean": 60.0,
        "trend": "stable",
        "anomaly_count": 0,
        "peak_count": 0,
        "variability": "low",
        "summary": "Resumo de teste.",
    }

    response = client.get("/api/v1/analysis", params={"limit": 1})

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "message" in response.json()
    assert isinstance(response.json()["data"], dict)
    assert response.json()["data"]["trend"] == "stable"
    mock_fetch_recent_signals.assert_called_once_with(limit=1, sensor_id=None)
    mock_analyze_signals.assert_called_once()


def test_signals_endpoint_returns_400_for_invalid_limit():
    response = client.get("/api/v1/signals", params={"limit": 0})

    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert "limit" in response.json()["message"]


def test_analysis_endpoint_returns_400_for_invalid_limit():
    response = client.get("/api/v1/analysis", params={"limit": 0})

    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert "limit" in response.json()["message"]


def test_signals_endpoint_returns_400_for_invalid_sensor_id():
    response = client.get("/api/v1/signals", params={"limit": 1, "sensor_id": ""})

    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert "sensor_id" in response.json()["message"]


@patch("app.routes.signals.fetch_recent_signals")
def test_signals_endpoint_returns_empty_message(mock_fetch_recent_signals):
    mock_fetch_recent_signals.return_value = []

    response = client.get("/api/v1/signals", params={"limit": 10})

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"] == []
    assert response.json()["message"] == "Nenhum dado encontrado"


def test_health_endpoint_returns_running_status():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": None,
        "data": {
            "service": "PlantPulse API",
            "status": "running",
        },
    }


def test_root_endpoint_returns_standard_response():
    response = client.get("/api/v1")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["message"] == "PlantPulse API em execucao."


@patch("app.routes.analysis.fetch_recent_signals")
@patch("app.routes.analysis.analyze_signals")
def test_analysis_endpoint_returns_empty_message_without_calling_analysis(
    mock_analyze_signals, mock_fetch_recent_signals
):
    mock_fetch_recent_signals.return_value = []

    response = client.get("/api/v1/analysis", params={"limit": 10})

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"] == []
    assert response.json()["message"] == "Nenhum dado encontrado"
    mock_analyze_signals.assert_not_called()
