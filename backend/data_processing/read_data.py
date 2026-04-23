from datetime import datetime


def _get_db_connection():
    from database.db_connection import get_db_connection

    return get_db_connection()


def _close_db_connection(connection) -> None:
    from database.db_connection import close_connection

    close_connection(connection)


def fetch_recent_signals(limit: int, sensor_id: str | None = None):
    if limit <= 0:
        raise ValueError("limit deve ser maior que zero.")

    connection = None
    cursor = None

    try:
        connection = _get_db_connection()
        cursor = connection.cursor()

        if sensor_id:
            cursor.execute(
                """
                SELECT
                    signal_timestamp,
                    sensor_id,
                    signal_value,
                    temperature,
                    humidity,
                    source
                FROM plant_signals
                WHERE sensor_id = %s
                ORDER BY signal_timestamp DESC
                LIMIT %s
                """,
                (sensor_id, limit),
            )
        else:
            cursor.execute(
                """
                SELECT
                    signal_timestamp,
                    sensor_id,
                    signal_value,
                    temperature,
                    humidity,
                    source
                FROM plant_signals
                ORDER BY signal_timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )

        rows = cursor.fetchall()
        ordered_rows = sorted(rows, key=lambda row: row[0])

        return [
            {
                "signal_timestamp": signal_timestamp,
                "sensor_id": row_sensor_id,
                "signal_value": float(signal_value),
                "temperature": float(temperature),
                "humidity": float(humidity),
                "source": source,
            }
            for signal_timestamp, row_sensor_id, signal_value, temperature, humidity, source in ordered_rows
        ]
    except Exception as error:
        raise RuntimeError(
            "Erro ao buscar sinais no PostgreSQL. "
            f"Causa original: {error}"
        ) from error
    finally:
        if cursor is not None:
            cursor.close()
        _close_db_connection(connection)
