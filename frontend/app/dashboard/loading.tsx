export default function DashboardLoading() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl items-center justify-center px-6 py-12">
      <div className="rounded-3xl border border-ink/10 bg-white/80 px-8 py-6 shadow-panel backdrop-blur">
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-moss">
          PlantPulse
        </p>
        <h1 className="mt-3 text-2xl font-semibold text-ink">
          Carregando dashboard...
        </h1>
        <p className="mt-2 text-sm text-ink/70">
          Buscando os sinais recentes e a analise mais atual.
        </p>
      </div>
    </main>
  );
}
