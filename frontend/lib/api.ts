export type SignalRecord = {
  signal_timestamp: string;
  sensor_id: string;
  signal_value: number;
  temperature: number;
  humidity: number;
  source: string;
};

export type AnalysisData = {
  total_records: number;
  signal_mean: number;
  signal_min: number;
  signal_max: number;
  signal_amplitude: number;
  temperature_mean: number;
  humidity_mean: number;
  trend: string;
  anomaly_count: number;
  peak_count: number;
  variability: string;
  summary: string;
};

export type SignalsApiResponse = {
  status: "success";
  data: SignalRecord[];
  message?: string | null;
};

export type AnalysisApiResponse = {
  status: "success";
  data: AnalysisData | null;
  message?: string | null;
};

type ErrorApiResponse = {
  status: "error";
  message: string;
};

type EmptyAnalysisResponse = {
  status: "success";
  data: [];
  message?: string | null;
};


const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000/api/v1";


export async function getSignals(
  limit: number,
  sensorId?: string,
): Promise<SignalsApiResponse> {
  return fetchApi<SignalsApiResponse>(buildPath("/signals", limit, sensorId));
}


export async function getAnalysis(
  limit: number,
  sensorId?: string,
): Promise<AnalysisApiResponse> {
  const payload = await fetchApi<AnalysisApiResponse | EmptyAnalysisResponse>(
    buildPath("/analysis", limit, sensorId),
  );

  if (Array.isArray(payload.data)) {
    return {
      status: payload.status,
      data: null,
      message: payload.message,
    };
  }

  return payload;
}


async function fetchApi<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
  });

  const payload = (await response.json()) as T | ErrorApiResponse;

  if (!response.ok) {
    const message =
      "message" in payload && payload.message
        ? payload.message
        : "Falha ao consultar a API do PlantPulse.";
    throw new Error(message);
  }

  return payload as T;
}


function buildPath(path: string, limit: number, sensorId?: string) {
  const params = new URLSearchParams({ limit: String(limit) });

  if (sensorId?.trim()) {
    params.set("sensor_id", sensorId.trim());
  }

  return `${path}?${params.toString()}`;
}
