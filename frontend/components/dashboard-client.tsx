"use client";

import { useEffect, useState } from "react";

import { SignalChart } from "@/components/chart";
import { StatsCard } from "@/components/stats-card";
import { Summary } from "@/components/summary";
import {
  type AnalysisData,
  type SignalRecord,
  getAnalysis,
  getSignals,
} from "@/lib/api";


const LIMIT_OPTIONS = [50, 100, 200];


export function DashboardClient() {
  const [limit, setLimit] = useState(100);
  const [sensorId, setSensorId] = useState("");
  const [appliedSensorId, setAppliedSensorId] = useState("");
  const [signals, setSignals] = useState<SignalRecord[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadDashboard() {
      setIsLoading(true);
      setError(null);

      try {
        const [signalsResponse, analysisResponse] = await Promise.all([
          getSignals(limit, appliedSensorId),
          getAnalysis(limit, appliedSensorId),
        ]);

        if (!isMounted) {
          return;
        }

        setSignals(signalsResponse.data);
        setAnalysis(analysisResponse.data);
        setMessage(
          signalsResponse.message ??
            analysisResponse.message ??
            (signalsResponse.data.length === 0
              ? "Nenhum dado encontrado"
              : null),
        );
      } catch (loadError) {
        if (!isMounted) {
          return;
        }

        setSignals([]);
        setAnalysis(null);
        setMessage(null);
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Nao foi possivel carregar o dashboard.",
        );
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      isMounted = false;
    };
  }, [limit, appliedSensorId]);

  function handleRefresh() {
    setAppliedSensorId(sensorId.trim());
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-10">
      <section className="rounded-[2rem] border border-ink/10 bg-white/80 p-8 shadow-panel backdrop-blur">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.24em] text-moss">
              PlantPulse Dashboard
            </p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight text-ink">
              Sinais recentes e leitura analitica
            </h1>
            <p className="mt-3 max-w-2xl text-base leading-7 text-ink/72">
              Visualizacao de sinais da API com leitura imediata de tendencia,
              variabilidade e anomalias.
            </p>
          </div>

          <div className="grid gap-3 rounded-[1.6rem] border border-ink/10 bg-sand/70 p-4 md:grid-cols-[180px_1fr_auto]">
            <label className="text-sm font-medium text-ink">
              Limite de registros
              <select
                className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-moss"
                value={limit}
                onChange={(event) => setLimit(Number(event.target.value))}
              >
                {LIMIT_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label className="text-sm font-medium text-ink">
              Sensor ID
              <input
                className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-moss"
                placeholder="Opcional"
                value={sensorId}
                onChange={(event) => setSensorId(event.target.value)}
              />
            </label>

            <button
              className="rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-ink/90 disabled:cursor-not-allowed disabled:bg-ink/45"
              onClick={handleRefresh}
              disabled={isLoading}
              type="button"
            >
              Atualizar dados
            </button>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3 text-sm text-ink/70">
          <span className="rounded-full bg-leaf/20 px-3 py-1">
            {isLoading ? "Atualizando..." : `${signals.length} registros carregados`}
          </span>
          {appliedSensorId ? (
            <span className="rounded-full bg-moss/15 px-3 py-1">
              Filtro por sensor: {appliedSensorId}
            </span>
          ) : (
            <span className="rounded-full bg-white/70 px-3 py-1">
              Sem filtro de sensor
            </span>
          )}
        </div>
      </section>

      {isLoading ? (
        <StatePanel
          eyebrow="Carregando"
          title="Buscando sinais e analise"
          description="Aguarde enquanto o dashboard atualiza os dados mais recentes."
          tone="moss"
        />
      ) : error ? (
        <StatePanel
          eyebrow="Erro de carregamento"
          title="O dashboard nao conseguiu consultar a API"
          description={error}
          tone="clay"
        />
      ) : !signals.length || !analysis ? (
        <StatePanel
          eyebrow="Sem dados"
          title="Nenhum resultado disponivel"
          description={
            message ?? "A API respondeu sem registros para os parametros atuais."
          }
          tone="sand"
        />
      ) : (
        <>
          <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatsCard
              label="Media do sinal"
              value={analysis.signal_mean.toFixed(2)}
              tone="leaf"
              helper={`Amplitude ${analysis.signal_amplitude.toFixed(2)}`}
            />
            <StatsCard
              label="Tendencia"
              value={translateTrend(analysis.trend)}
              tone="moss"
              helper="Comparacao entre as duas metades da serie"
            />
            <StatsCard
              label="Variabilidade"
              value={translateVariability(analysis.variability)}
              tone="sand"
              helper="Classificacao baseada no desvio padrao relativo"
            />
            <StatsCard
              label="Anomalias"
              value={String(analysis.anomaly_count)}
              tone="clay"
              helper="Desvios relevantes em torno da media"
            />
          </section>

          <section className="mt-8 grid gap-8 xl:grid-cols-[minmax(0,1.6fr)_minmax(280px,0.9fr)]">
            <div className="rounded-[2rem] border border-ink/10 bg-white/82 p-6 shadow-panel">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-semibold text-ink">
                    Evolucao do sinal
                  </h2>
                  <p className="mt-1 text-sm text-ink/68">
                    Linha temporal de signal_value com base nos dados mais recentes.
                  </p>
                </div>
              </div>
              <SignalChart data={signals} />
            </div>

            <div className="space-y-6">
              <Summary text={analysis.summary} />

              <div className="rounded-[2rem] border border-ink/10 bg-white/82 p-6 shadow-panel">
                <h2 className="text-xl font-semibold text-ink">Faixas observadas</h2>
                <div className="mt-5 grid gap-3">
                  <MiniStat label="Sinal minimo" value={analysis.signal_min.toFixed(2)} />
                  <MiniStat label="Sinal maximo" value={analysis.signal_max.toFixed(2)} />
                  <MiniStat
                    label="Temp. media"
                    value={`${analysis.temperature_mean.toFixed(2)} C`}
                  />
                  <MiniStat
                    label="Umidade media"
                    value={`${analysis.humidity_mean.toFixed(2)} %`}
                  />
                </div>
              </div>
            </div>
          </section>
        </>
      )}
    </main>
  );
}


function StatePanel({
  eyebrow,
  title,
  description,
  tone,
}: {
  eyebrow: string;
  title: string;
  description: string;
  tone: "moss" | "clay" | "sand";
}) {
  const toneClass =
    tone === "clay"
      ? "border-clay/25 text-clay"
      : tone === "sand"
        ? "border-ink/10 text-moss"
        : "border-moss/25 text-moss";

  return (
    <section className="mt-8 flex justify-center">
      <div
        className={`max-w-xl rounded-[2rem] border bg-white/90 p-8 shadow-panel ${toneClass}`}
      >
        <p className="text-sm font-medium uppercase tracking-[0.24em]">{eyebrow}</p>
        <h2 className="mt-3 text-3xl font-semibold text-ink">{title}</h2>
        <p className="mt-3 text-base leading-7 text-ink/75">{description}</p>
      </div>
    </section>
  );
}


function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-ink/10 bg-sand/60 px-4 py-3">
      <p className="text-sm text-ink/65">{label}</p>
      <p className="mt-1 text-lg font-semibold text-ink">{value}</p>
    </div>
  );
}


function translateTrend(trend: string) {
  switch (trend) {
    case "rising":
      return "Alta";
    case "falling":
      return "Queda";
    default:
      return "Estavel";
  }
}


function translateVariability(variability: string) {
  switch (variability) {
    case "low":
      return "Baixa";
    case "medium":
      return "Media";
    default:
      return "Alta";
  }
}
