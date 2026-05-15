import type { ValidationIssue } from '../types'

export default function IssueList({ issues, onSelect }: { issues: ValidationIssue[]; onSelect?: (field?: string) => void }){
  if(!issues.length){
    return <div className="text-sm text-steel">No issues found.</div>
  }

  return (
    <ul className="space-y-3">
      {issues.map((issue) => {
        const tone = issue.severity === 'error'
          ? 'border-red-400 bg-red-50'
          : issue.severity === 'warning'
            ? 'border-yellow-300 bg-yellow-50'
            : 'border-black/10 bg-white'
        return (
          <li key={issue.id} className={`rounded-xl border p-3 ${tone}`}>
            <button onClick={()=> onSelect?.(issue.field_name)} className="text-left w-full">
              <div className="text-sm font-semibold">{issue.field_name || 'General'}</div>
              <div className="text-xs text-steel">{issue.issue_type}</div>
              <div className="text-sm mt-1">{issue.message}</div>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
