import type { LineItem } from '../types'

export default function LineItemsTable({
  items,
  onChange,
}: {
  items: LineItem[]
  onChange: (items: LineItem[]) => void
}){
  function update(idx: number, field: keyof LineItem, value: string){
    const next = [...items]
    const item = { ...next[idx] }
    if(field === 'quantity' || field === 'unit_price' || field === 'line_total'){
      item[field] = value === '' ? undefined : Number(value)
    } else {
      item[field] = value as any
    }
    next[idx] = item
    onChange(next)
  }

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-widest text-steel">Line items</div>
        <button
          className="text-sm px-3 py-1 rounded-full border border-black/10"
          onClick={()=> onChange([...items, { description: '', quantity: 1, unit_price: 0, line_total: 0 }])}
        >
          Add row
        </button>
      </div>
      <div className="mt-2 overflow-x-auto">
        <table className="w-full text-sm bg-white rounded-xl">
          <thead className="bg-white">
            <tr className="text-left text-steel">
              <th className="p-2">Description</th>
              <th>Qty</th>
              <th>Unit</th>
              <th>Line total</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={idx} className="border-t border-black/5">
                <td className="p-2">
                  <input className="w-full border rounded px-2 py-1" value={item.description || ''} onChange={(e)=> update(idx, 'description', e.target.value)} />
                </td>
                <td className="p-2">
                  <input type="number" className="w-20 border rounded px-2 py-1" value={item.quantity ?? ''} onChange={(e)=> update(idx, 'quantity', e.target.value)} />
                </td>
                <td className="p-2">
                  <input type="number" className="w-24 border rounded px-2 py-1" value={item.unit_price ?? ''} onChange={(e)=> update(idx, 'unit_price', e.target.value)} />
                </td>
                <td className="p-2">
                  <input type="number" className="w-28 border rounded px-2 py-1" value={item.line_total ?? ''} onChange={(e)=> update(idx, 'line_total', e.target.value)} />
                </td>
                <td className="p-2">
                  <button className="text-xs text-red-600" onClick={()=> onChange(items.filter((_, i)=> i !== idx))}>Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
