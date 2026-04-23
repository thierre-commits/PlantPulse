CREATE TABLE IF NOT EXISTS plant_signals (
    id BIGSERIAL PRIMARY KEY,
    signal_timestamp TIMESTAMP NOT NULL,
    sensor_id VARCHAR(100) NOT NULL,
    signal_value NUMERIC(10, 4) NOT NULL,
    temperature NUMERIC(5, 2),
    humidity NUMERIC(5, 2),
    source VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT plant_signals_sensor_timestamp_unique UNIQUE (sensor_id, signal_timestamp)
);
