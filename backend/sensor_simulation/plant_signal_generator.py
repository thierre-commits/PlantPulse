import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


EXPECTED_COLUMNS = [
    "signal_timestamp",
    "sensor_id",
    "signal_value",
    "temperature",
    "humidity",
    "source",
]


def _validate_export_row(row, index: int) -> None:
    row_columns = set(row.keys())
    expected_columns = set(EXPECTED_COLUMNS)

    if row_columns != expected_columns:
        raise ValueError(
            "Estrutura invalida em data. Cada item deve conter exatamente "
            "as colunas: signal_timestamp, sensor_id, signal_value, "
            "temperature, humidity, source. "
            f"Item com erro no indice {index}."
        )

    if not isinstance(row["signal_timestamp"], str) or not row["signal_timestamp"].strip():
        raise ValueError(
            "Tipo invalido em data. signal_timestamp deve ser uma string nao vazia. "
            f"Item com erro no indice {index}."
        )

    if not isinstance(row["sensor_id"], str) or not row["sensor_id"].strip():
        raise ValueError(
            "Tipo invalido em data. sensor_id deve ser uma string nao vazia. "
            f"Item com erro no indice {index}."
        )

    if not isinstance(row["signal_value"], (int, float)):
        raise ValueError(
            "Tipo invalido em data. signal_value deve ser int ou float. "
            f"Item com erro no indice {index}."
        )

    if not isinstance(row["temperature"], (int, float)):
        raise ValueError(
            "Tipo invalido em data. temperature deve ser int ou float. "
            f"Item com erro no indice {index}."
        )

    if not isinstance(row["humidity"], (int, float)):
        raise ValueError(
            "Tipo invalido em data. humidity deve ser int ou float. "
            f"Item com erro no indice {index}."
        )

    if not isinstance(row["source"], str) or not row["source"].strip():
        raise ValueError(
            "Tipo invalido em data. source deve ser uma string nao vazia. "
            f"Item com erro no indice {index}."
        )


def generate_signals(
    num_points: int,
    sensor_id: str,
    start_time: datetime,
    interval_seconds: int,
    seed: Optional[int] = None,
):
    if num_points <= 0:
        raise ValueError("num_points deve ser maior que zero.")

    if interval_seconds <= 0:
        raise ValueError("interval_seconds deve ser maior que zero.")

    if not sensor_id:
        raise ValueError("sensor_id nao pode ser vazio.")

    generated_data = []
    random_generator = random.Random(seed)

    for index in range(num_points):
        current_time = start_time + timedelta(seconds=index * interval_seconds)
        cycle_position = index / 8
        trend_factor = min(index * 0.03, 6.0)

        # Nesta etapa mantemos o timestamp como string para gerar um CSV
        # diretamente compativel e simples, sem uma etapa extra de serializacao.
        signal_base = 50 + 18 * math.sin(cycle_position)
        signal_noise = random_generator.uniform(-2.5, 2.5)
        signal_value = _clamp(signal_base + signal_noise + trend_factor, 0, 100)

        temperature_base = 24 + 4 * math.sin(cycle_position / 2 + 0.8)
        temperature_noise = random_generator.uniform(-0.8, 0.8)
        temperature = _clamp(temperature_base + temperature_noise, 15, 35)

        humidity_base = 62 + 12 * math.cos(cycle_position / 2)
        humidity_noise = random_generator.uniform(-3.0, 3.0)
        humidity = _clamp(humidity_base - trend_factor / 3 + humidity_noise, 30, 90)

        generated_data.append(
            {
                "signal_timestamp": current_time.isoformat(sep=" "),
                "sensor_id": sensor_id,
                "signal_value": round(signal_value, 4),
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "source": "simulation",
            }
        )

    return generated_data


def export_to_csv(data, filepath):
    if not data:
        raise ValueError("data nao pode ser vazio.")

    for index, row in enumerate(data):
        _validate_export_row(row, index)

    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    output_file = project_root / "data" / "simulated_signals.csv"

    sample_data = generate_signals(
        num_points=96,
        sensor_id="sensor_001",
        start_time=datetime(2026, 4, 22, 8, 0, 0),
        interval_seconds=900,
        seed=42,
    )
    export_to_csv(sample_data, output_file)

    print(f"CSV gerado com sucesso em: {output_file}")
