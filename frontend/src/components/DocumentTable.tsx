import type { DocumentData } from '../types'
import StatusBadge from './StatusBadge'
import { Link } from 'react-router-dom'

export default function DocumentTable({ items }: { items: DocumentData[] }){
  return (
    <div className="card rounded-2xl overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-white">
          <tr className="text-left text-steel">
            <th className="p-3">Number</th>
            <th>Supplier</th>
            <th>Type</th>
            <th>Currency</th>
            <th>Total</th>
            <th>Status</th>
            <th>Uploaded</th>
          </tr>
        </thead>
        <tbody>
          {items.map((doc) => (
            <tr key={doc.id} className="border-t border-black/5 bg-white/70">
              <td className="p-3">
                <Link to={`/documents/${doc.id}`} className="text-blue-700 font-medium">
                  {doc.document_number || doc.id}
                </Link>
              </td>
              <td>{doc.supplier_name || '-'}</td>
              <td>{doc.doc_type || '-'}</td>
              <td>{doc.currency || '-'}</td>
              <td>{doc.total ?? '-'}</td>
              <td><StatusBadge status={doc.status} /></td>
              <td>{doc.created_at?.slice(0, 10) || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
