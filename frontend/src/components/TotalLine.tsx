/** Total affiché en haut d'une liste. */
export function TotalLine({ label, amount }: { label: string; amount: string }) {
  return (
    <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 rounded-xl bg-surface-sidebar px-4 py-3">
      <span className="text-ink-gray-6">{label}</span>
      <span className="text-xl font-semibold text-ink-gray-9 tabular">{amount}</span>
    </div>
  );
}
