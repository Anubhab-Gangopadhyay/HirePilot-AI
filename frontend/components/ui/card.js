export function Card({ title, value, hint, tone = "default", children }) {
  const toneClass = tone === "brand" ? "from-teal-600/15 to-transparent" : tone === "warm" ? "from-orange-500/15 to-transparent" : "from-black/5 to-transparent";
  return (
    <div className={`rounded-[1.75rem] border border-[var(--line)] bg-gradient-to-br ${toneClass} bg-[var(--panel)] p-5 shadow-[0_20px_60px_rgba(24,35,15,0.06)]`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-[var(--muted)]">{title}</p>
          {value ? <h3 className="mt-2 text-3xl font-semibold">{value}</h3> : null}
          {hint ? <p className="mt-2 text-sm text-[var(--muted)]">{hint}</p> : null}
        </div>
      </div>
      {children ? <div className="mt-4">{children}</div> : null}
    </div>
  );
}
