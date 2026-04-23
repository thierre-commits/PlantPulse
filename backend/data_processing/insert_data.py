import csv
from datetime import datetime
from pathlib import Path

from sensor_simulation.plant_signal_generator import EXPECTED_COLUMNS

INSERT_BATCH_SIZE = 500
INSERT_SIGNALS_QUERY = """
INSERT INTO plant_signals (
    signal_timestamp,
    sensor_id,
    signal_value,
    temperature,
    humidity,
    source
)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (sensor_id, signal_timestamp) DO NOTHING
"""


def _get_db_connection():
    from database.db_connection import get_db_connection

    return get_db_connection()


def _close_db_connection(connection) -> None:
    from database.db_connection import close_connection

    close_connection(connection)


def load_csv(filepath):
    input_path = Path(filepath)

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo CSV nao encontrado: {input_path}")

    with input_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []

        # Nesta etapa exigimos exatamente as colunas esperadas para manter o
        # contrato do CSV previsivel e alinhado com as etapas anteriores.
        if set(fieldnames) != set(EXPECTED_COLUMNS):
            raise ValueError(
                "CSV invalido. O arquivo deve conter exatamente as colunas: "
                "signal_timestamp, sensor_id, signal_value, temperature, "
                "humidity, source."
            )

        return list(reader)


def _prepare_signal_row(row, index: int):
    try:
        signal_timestamp = row["signal_timestamp"].strip()
        sensor_id = row["sensor_id"].strip()
        source = row["source"].strip()

        if not signal_timestamp:
            raise ValueError("signal_timestamp nao pode ser vazio.")

        if not sensor_id:
            raise ValueError("sensor_id nao pode ser vazio.")

        if not source:
            raise ValueError("source nao pode ser vazio.")

        return (
            datetime.fromisoformat(signal_timestamp),
            sensor_id,
            float(row["signal_value"]),
            float(row["temperature"]),
            float(row["humidity"]),
            source,
        )
    except KeyError as error:
        raise ValueError(
            f"Registro invalido no indice {index}. Coluna ausente: {error.args[0]}"
        ) from error
    except ValueError as error:
        raise ValueError(
            f"Registro invalido no indice {index}: {error}"
        ) from error


def _chunk_rows(rows, batch_size: int):
    for start in range(0, len(rows), batch_size):
        yield rows[start : start + batch_size]


def insert_signals(data):
    if not data:
        raise ValueError("data nao pode ser vazio.")

    prepared_rows = [_prepare_signal_row(row, index) for index, row in enumerate(data)]

    connection = None
    cursor = None

    try:
        connection = _get_db_connection()
        cursor = connection.cursor()
        for batch in _chunk_rows(prepared_rows, INSERT_BATCH_SIZE):
            cursor.executemany(INSERT_SIGNALS_QUERY, batch)
        connection.commit()
    except Exception as error:
        if connection is not None:
            connection.rollback()
        raise RuntimeError(
            "Erro ao inserir sinais no PostgreSQL. "
            f"Causa original: {error}. A transacao foi revertida."
        ) from error
    finally:
        if cursor is not None:
            cursor.close()
        _close_db_connection(connection)


def main() -> None:
    from dotenv import load_dotenv

    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "simulated_signals.csv"

    try:
        load_dotenv()
        data = load_csv(csv_path)
        # Duplicatas do mesmo sensor no mesmo instante sao ignoradas pelo banco.
        insert_signals(data)
        print("Dados inseridos no PostgreSQL com sucesso.")
    except Exception as error:
        print(f"Erro ao processar insercao do CSV: {error}")


if __name__ == "__main__":
    main()
