export interface LineItem {
  id?: string
  description?: string
  quantity?: number
  unit_price?: number
  line_total?: number
}

export interface ValidationIssue {
  id?: string
  field_name?: string
  issue_type?: string
  message?: string
  severity?: 'info' | 'warning' | 'error'
}

export interface DocumentData {
  id: string
  status: string
  doc_type?: string
  supplier_name?: string
  document_number?: string
  issue_date?: string
  due_date?: string
  currency?: string
  subtotal?: number
  tax?: number
  total?: number
  raw_text?: string
  file_path?: string
  line_items?: LineItem[]
  validation_issues?: ValidationIssue[]
  created_at?: string
}

export interface Envelope<T> {
  data: T | null
  errors: { field?: string; message: string }[]
}

export interface DocumentList {
  items: DocumentData[]
  meta: { page: number; page_size: number; total: number }
}

export interface DashboardSummary {
  counts: Record<string, number>
  totals: Record<string, number>
}
