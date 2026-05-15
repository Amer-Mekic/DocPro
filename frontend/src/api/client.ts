import type { DocumentData, DocumentList, Envelope, DashboardSummary } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function parseJson(res: Response){
  const json = await res.json().catch(() => null)
  if(!res.ok){
    const msg = json?.errors?.[0]?.message || res.statusText
    throw new Error(msg)
  }
  return json
}

export async function uploadDocument(file: File, onProgress?: (p: number)=>void){
  return new Promise<Envelope<{id:string; status:string; file_path:string; created_at:string}>>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_URL}/documents/upload`)
    xhr.onload = () => {
      try{ resolve(JSON.parse(xhr.responseText)) }catch(e){ reject(e) }
    }
    xhr.onerror = () => reject(new Error('Network error'))
    if(xhr.upload && onProgress){
      xhr.upload.onprogress = (ev)=>{
        if(ev.lengthComputable){
          onProgress(Math.round((ev.loaded / ev.total) * 100))
        }
      }
    }
    const fd = new FormData()
    fd.append('file', file)
    xhr.send(fd)
  })
}

export async function listDocuments(page=1, page_size=20, status?: string){
  const params = new URLSearchParams({ page: String(page), page_size: String(page_size) })
  if(status) params.set('status', status)
  const res = await fetch(`${API_URL}/documents?${params.toString()}`)
  return parseJson(res) as Promise<Envelope<DocumentList>>
}

export async function getDocument(id: string){
  const res = await fetch(`${API_URL}/documents/${id}`)
  return parseJson(res) as Promise<Envelope<DocumentData>>
}

export async function patchDocument(id: string, payload: Partial<DocumentData> & { line_items?: any[] }){
  const res = await fetch(`${API_URL}/documents/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return parseJson(res) as Promise<Envelope<DocumentData>>
}

export async function validateDocument(id: string){
  const res = await fetch(`${API_URL}/documents/${id}/validate`, { method: 'POST' })
  return parseJson(res) as Promise<Envelope<DocumentData>>
}

export async function confirmDocument(id: string){
  const res = await fetch(`${API_URL}/documents/${id}/confirm`, { method: 'POST' })
  return parseJson(res) as Promise<Envelope<DocumentData>>
}

export async function rejectDocument(id: string){
  const res = await fetch(`${API_URL}/documents/${id}/reject`, { method: 'POST' })
  return parseJson(res) as Promise<Envelope<DocumentData>>
}

export async function dashboardSummary(){
  const res = await fetch(`${API_URL}/documents/dashboard/summary`)
  return parseJson(res) as Promise<Envelope<DashboardSummary>>
}
