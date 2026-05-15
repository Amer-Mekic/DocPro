import type { DashboardSummary } from '../types'

export default function SummaryStrip({ summary }: { summary: DashboardSummary }){
  const counts = Object.entries(summary.counts || {})
  const totals = Object.entries(summary.totals || {})

  return (
    <div className="card rounded-2xl p-4 md:p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <div className="text-xs uppercase tracking-widest text-steel">Counts</div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {counts.map(([key, val]) => (
              <div key={key} className="rounded-xl bg-white p-3 border border-black/5">
                <div className="text-sm text-steel">{key}</div>
                <div className="text-xl font-display">{val}</div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="text-xs uppercase tracking-widest text-steel">Totals</div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {totals.map(([key, val]) => (
              <div key={key} className="rounded-xl bg-white p-3 border border-black/5">
                <div className="text-sm text-steel">{key}</div>
                <div className="text-xl font-display">{val}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
