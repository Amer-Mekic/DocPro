from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    status: str
    doc_type: str | None
    supplier_name: str | None
    document_number: str | None
    issue_date: date | None
    due_date: date | None
    currency: str | None
    subtotal: Decimal | None
    tax: Decimal | None
    total: Decimal | None
    raw_text: str | None
    file_path: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    id: UUID
    status: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class LineItemUpdate(BaseModel):
    description: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    line_total: Decimal | None = None


class DocumentPatchRequest(BaseModel):
    doc_type: str | None = None
    supplier_name: str | None = None
    document_number: str | None = None
    issue_date: date | None = None
    due_date: date | None = None
    currency: str | None = None
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    total: Decimal | None = None
    line_items: list[LineItemUpdate] | None = None