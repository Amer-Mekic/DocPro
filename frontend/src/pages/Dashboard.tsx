import { useEffect, useState } from 'react'
import { listDocuments, dashboardSummary } from '../api/client'
import type { DocumentData, DashboardSummary } from '../types'
import DocumentTable from '../components/DocumentTable'
import SummaryStrip from '../components/SummaryStrip'

const STATUSES = ['uploaded', 'needs_review', 'validated', 'rejected']

export default function Dashboard(){
  const [items, setItems] = useState<DocumentData[]>([])
  const [summary, setSummary] = useState<DashboardSummary>({ counts: {}, totals: {} })
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)

  useEffect(() => {
    async function load(){
      const res = await listDocuments(1, 200, statusFilter)
      const next = res.data?.items || []
      const filtered = statusFilter ? next.filter((doc) => doc.status === statusFilter) : next
      setItems(filtered)
    }
    async function loadSummary(){
      const res = await dashboardSummary()
      setSummary(res.data || { counts: {}, totals: {} })
    }
    load()
    loadSummary()
  }, [statusFilter])

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-widest text-steel">Dashboard</div>
          <h2 className="text-2xl font-display">Document flow</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className={`px-3 py-1 rounded-full border ${statusFilter ? 'border-black/10' : 'bg-ink text-white'}`} onClick={()=> setStatusFilter(undefined)}>All</button>
          {STATUSES.map((status) => (
            <button key={status} className={`px-3 py-1 rounded-full border border-black/10 ${statusFilter === status ? 'bg-ink text-white' : 'bg-white'}`} onClick={()=> setStatusFilter(status)}>
              {status} ({summary.counts[status] || 0})
            </button>
          ))}
        </div>
      </div>

      <SummaryStrip summary={summary} />
      <DocumentTable items={items} />
    </div>
  )
}
