import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { confirmDocument, getDocument, patchDocument, rejectDocument, validateDocument } from '../api/client'
import type { DocumentData, ValidationIssue } from '../types'
import FieldInput from '../components/FieldInput'
import type { IssueSeverity } from '../components/FieldInput'
import IssueList from '../components/IssueList'
import LineItemsTable from '../components/LineItemsTable'
import ActionBar from '../components/ActionBar'

const DOC_TYPES = ['invoice', 'purchase_order']

export default function Review(){
  const { id } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState<DocumentData | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  const fieldRefs = {
    supplier_name: useRef<HTMLDivElement>(null),
    document_number: useRef<HTMLDivElement>(null),
    doc_type: useRef<HTMLDivElement>(null),
    issue_date: useRef<HTMLDivElement>(null),
    due_date: useRef<HTMLDivElement>(null),
    currency: useRef<HTMLDivElement>(null),
    subtotal: useRef<HTMLDivElement>(null),
    tax: useRef<HTMLDivElement>(null),
    total: useRef<HTMLDivElement>(null),
  }

  useEffect(() => {
    async function load(){
      if(!id) return
      const res = await getDocument(id)
      setDoc(res.data)
    }
    load()
  }, [id])

  const issueMap = useMemo(() => {
    const map: Record<string, ValidationIssue> = {}
    ;(doc?.validation_issues || []).forEach((issue) => {
      if(issue.field_name) map[issue.field_name] = issue
    })
    return map
  }, [doc])

  function getSeverity(field: string): IssueSeverity {
    const issue = issueMap[field]
    return issue?.severity
  }

  function setField(field: keyof DocumentData, value: any){
    setDoc((prev) => prev ? { ...prev, [field]: value } : prev)
  }

  async function save(){
    if(!doc || !id) return
    setSaving(true)
    setSaveError(null)
    try{
      await patchDocument(id, {
        supplier_name: doc.supplier_name,
        document_number: doc.document_number,
        doc_type: doc.doc_type,
        issue_date: doc.issue_date,
        due_date: doc.due_date,
        currency: doc.currency,
        subtotal: doc.subtotal,
        tax: doc.tax,
        total: doc.total,
        line_items: doc.line_items || [],
      })
      const refreshed = await getDocument(id)
      setDoc(refreshed.data)
    }catch(error){
      const message = error instanceof Error ? error.message : 'Save failed'
      setSaveError(message)
    }finally{
      setSaving(false)
    }
  }

  async function doConfirm(){
    if(!id) return
    await confirmDocument(id)
    navigate('/')
  }

  async function doReject(){
    if(!id) return
    await rejectDocument(id)
    navigate('/')
  }

  async function doValidate(){
    if(!id) return
    await validateDocument(id)
    const refreshed = await getDocument(id)
    setDoc(refreshed.data)
  }

  function jumpToField(field?: string){
    if(!field) return
    const ref = (fieldRefs as any)[field]
    ref?.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  if(!doc){
    return <div className="text-sm text-steel">Loading document...</div>
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <div className="card rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-widest text-steel">Review</div>
              <h2 className="text-2xl font-display">{doc.document_number || doc.id}</h2>
            </div>
            <div className="text-xs text-steel">Status: {doc.status}</div>
          </div>
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div ref={fieldRefs.supplier_name}>
              <FieldInput label="Supplier" value={doc.supplier_name || ''} severity={getSeverity('supplier_name')} onChange={(v)=> setField('supplier_name', v)} />
            </div>
            <div ref={fieldRefs.document_number}>
              <FieldInput label="Document number" value={doc.document_number || ''} severity={getSeverity('document_number')} onChange={(v)=> setField('document_number', v)} />
            </div>
            <div ref={fieldRefs.doc_type}>
              <label className="block">
                <div className="text-xs uppercase tracking-widest text-steel mb-1">Doc type</div>
                <select
                  value={doc.doc_type || ''}
                  onChange={(e)=> setField('doc_type', e.target.value)}
                  className={`w-full rounded-lg border px-3 py-2 ${getSeverity('doc_type') ? 'border-yellow-300 bg-yellow-50' : 'border-black/10 bg-white'}`}
                >
                  <option value="">Select type</option>
                  {DOC_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </label>
            </div>
            <div ref={fieldRefs.currency}>
              <FieldInput label="Currency" value={doc.currency || ''} severity={getSeverity('currency')} onChange={(v)=> setField('currency', v)} />
            </div>
            <div ref={fieldRefs.issue_date}>
              <FieldInput label="Issue date" type="date" value={doc.issue_date?.slice(0,10) || ''} severity={getSeverity('issue_date')} onChange={(v)=> setField('issue_date', v)} />
            </div>
            <div ref={fieldRefs.due_date}>
              <FieldInput label="Due date" type="date" value={doc.due_date?.slice(0,10) || ''} severity={getSeverity('due_date')} onChange={(v)=> setField('due_date', v)} />
            </div>
            <div ref={fieldRefs.subtotal}>
              <FieldInput label="Subtotal" type="number" value={doc.subtotal ?? ''} severity={getSeverity('subtotal')} onChange={(v)=> setField('subtotal', v === '' ? undefined : Number(v))} />
            </div>
            <div ref={fieldRefs.tax}>
              <FieldInput label="Tax" type="number" value={doc.tax ?? ''} severity={getSeverity('tax')} onChange={(v)=> setField('tax', v === '' ? undefined : Number(v))} />
            </div>
            <div ref={fieldRefs.total}>
              <FieldInput label="Total" type="number" value={doc.total ?? ''} severity={getSeverity('total')} onChange={(v)=> setField('total', v === '' ? undefined : Number(v))} />
            </div>
          </div>

          <LineItemsTable items={doc.line_items || []} onChange={(items)=> setField('line_items', items)} />
          {saveError ? (
            <div className="text-xs text-red-600 mb-3">Save failed: {saveError}</div>
          ) : null}
          <ActionBar saving={saving} onSave={save} onValidate={doValidate} onConfirm={doConfirm} onReject={doReject} />
        </div>
      </div>

      <aside className="card rounded-2xl p-6 h-fit">
        <div className="text-xs uppercase tracking-widest text-steel">Validation</div>
        <h3 className="text-lg font-display mb-4">Issues</h3>
        <IssueList issues={doc.validation_issues || []} onSelect={jumpToField} />
      </aside>
    </div>
  )
}
