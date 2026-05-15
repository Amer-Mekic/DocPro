export type IssueSeverity = 'info' | 'warning' | 'error' | undefined

export default function FieldInput({
  label,
  value,
  onChange,
  type = 'text',
  severity,
}: {
  label: string
  value: string | number
  onChange: (val: string) => void
  type?: string
  severity?: IssueSeverity
}){
  const ring = severity === 'error'
    ? 'border-red-400 bg-red-50'
    : severity === 'warning'
      ? 'border-yellow-300 bg-yellow-50'
      : 'border-black/10 bg-white'

  return (
    <label className="block">
      <div className="text-xs uppercase tracking-widest text-steel mb-1">{label}</div>
      <input
        type={type}
        value={value}
        onChange={(e)=> onChange(e.target.value)}
        className={`w-full rounded-lg border px-3 py-2 ${ring}`}
      />
    </label>
  )
}
