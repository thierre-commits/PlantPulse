from statistics import mean, pstdev


TREND_TOLERANCE_PERCENT = 0.05
ANOMALY_STD_FACTOR = 1.5
LOW_VARIABILITY_CV = 0.05
MEDIUM_VARIABILITY_CV = 0.15


def analyze_signals(data):
    if not data:
        raise ValueError("data nao pode ser vazio.")

    signal_values = [float(row["signal_value"]) for row in data]
    temperature_values = [float(row["temperature"]) for row in data]
    humidity_values = [float(row["humidity"]) for row in data]

    total_records = len(data)
    signal_mean = mean(signal_values)
    signal_min = min(signal_values)
    signal_max = max(signal_values)
    signal_amplitude = signal_max - signal_min
    temperature_mean = mean(temperature_values)
    humidity_mean = mean(humidity_values)

    half_index = total_records // 2
    first_half = signal_values[:half_index] or signal_values
    second_half = signal_values[half_index:] or signal_values

    first_half_mean = mean(first_half)
    second_half_mean = mean(second_half)
    mean_difference = second_half_mean - first_half_mean
    trend_tolerance = abs(signal_mean) * TREND_TOLERANCE_PERCENT

    if mean_difference > trend_tolerance:
        trend = "rising"
    elif mean_difference < -trend_tolerance:
        trend = "falling"
    else:
        trend = "stable"

    signal_std = pstdev(signal_values)
    anomaly_count = sum(
        1
        for value in signal_values
        if abs(value - signal_mean) > ANOMALY_STD_FACTOR * signal_std
    )

    if signal_mean == 0:
        coefficient_of_variation = 0.0 if signal_std == 0 else float("inf")
    else:
        coefficient_of_variation = signal_std / abs(signal_mean)

    if coefficient_of_variation <= LOW_VARIABILITY_CV:
        variability = "low"
        variability_message = "baixa variabilidade"
    elif coefficient_of_variation <= MEDIUM_VARIABILITY_CV:
        variability = "medium"
        variability_message = "media variabilidade"
    else:
        variability = "high"
        variability_message = "alta variabilidade"

    trend_messages = {
        "rising": "o sinal apresenta tendencia de alta",
        "falling": "o sinal apresenta tendencia de queda",
        "stable": "o sinal esta relativamente estavel",
    }

    if anomaly_count == 0:
        anomaly_message = "sem anomalias relevantes detectadas"
    elif anomaly_count == 1:
        anomaly_message = "com 1 anomalia detectada"
    else:
        anomaly_message = f"com {anomaly_count} anomalias detectadas"

    summary = (
        f"Foram analisados {total_records} registros; "
        f"{trend_messages[trend]}, com media de sinal {signal_mean:.2f}, "
        f"{variability_message}, amplitude de {signal_amplitude:.2f} e "
        f"{anomaly_message}."
    )

    return {
        "total_records": total_records,
        "signal_mean": round(signal_mean, 4),
        "signal_min": round(signal_min, 4),
        "signal_max": round(signal_max, 4),
        "signal_amplitude": round(signal_amplitude, 4),
        "temperature_mean": round(temperature_mean, 4),
        "humidity_mean": round(humidity_mean, 4),
        "trend": trend,
        "anomaly_count": anomaly_count,
        "peak_count": anomaly_count,
        "variability": variability,
        "summary": summary,
    }
