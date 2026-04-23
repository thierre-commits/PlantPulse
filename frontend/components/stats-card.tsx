type StatsCardProps = {
  label: string;
  value: string;
  helper: string;
  tone: "leaf" | "moss" | "sand" | "clay";
};


const toneClasses: Record<StatsCardProps["tone"], string> = {
  leaf: "bg-leaf/25 text-ink",
  moss: "bg-moss/15 text-ink",
  sand: "bg-sand text-ink",
  clay: "bg-clay/15 text-ink",
};


export function StatsCard({ label, value, helper, tone }: StatsCardProps) {
  return (
    <article className="rounded-[1.6rem] border border-ink/10 bg-white/70 p-5 shadow-panel">
      <div
        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${toneClasses[tone]}`}
      >
        {label}
      </div>
      <p className="mt-5 text-3xl font-semibold tracking-tight text-ink">{value}</p>
      <p className="mt-2 text-sm leading-6 text-ink/68">{helper}</p>
    </article>
  );
}
