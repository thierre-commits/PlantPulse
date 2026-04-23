type SummaryProps = {
  text: string;
};


export function Summary({ text }: SummaryProps) {
  return (
    <section className="rounded-[2rem] border border-moss/15 bg-gradient-to-br from-moss/10 via-white to-leaf/20 p-6 shadow-panel">
      <p className="text-sm font-medium uppercase tracking-[0.22em] text-moss">
        Insight da analise
      </p>
      <h2 className="mt-3 text-2xl font-semibold text-ink">
        Leitura interpretativa do sinal
      </h2>
      <p className="mt-4 text-base leading-8 text-ink/78">{text}</p>
    </section>
  );
}
