from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from typing import Any, List, Dict


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


class ErrorItem(BaseModel):
    field: str | None = None
    message: str


class Envelope(BaseModel):
    data: Any | None = None
    errors: List[ErrorItem] = []


class DocumentEnvelope(BaseModel):
    data: DocumentResponse | None = None
    errors: List[ErrorItem] = []

    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "status": "validated",
                    "doc_type": "invoice",
                    "supplier_name": "ACME Corp",
                    "document_number": "INV-100",
                    "issue_date": "2026-05-01",
                    "due_date": "2026-05-15",
                    "currency": "USD",
                    "subtotal": 100.0,
                    "tax": 10.0,
                    "total": 110.0,
                    "raw_text": "...",
                    "file_path": "uploads/000.png",
                    "line_items": [
                        {"id": "00000000-0000-0000-0000-000000000001", "description": "Item A", "quantity": 1, "unit_price": 100.0, "line_total": 100.0}
                    ],
                    "validation_issues": [],
                    "created_at": "2026-05-15T12:00:00Z",
                },
                "errors": [],
            }
        }


class DocumentListEnvelope(BaseModel):
    data: Dict[str, Any]
    errors: List[ErrorItem] = []

    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "items": [
                        {
                            "id": "00000000-0000-0000-0000-000000000000",
                            "status": "validated",
                            "doc_type": "invoice",
                            "supplier_name": "ACME Corp",
                            "document_number": "INV-100",
                            "total": 110.0,
                            "currency": "USD",
                            "created_at": "2026-05-15T12:00:00Z",
                        }
                    ],
                    "meta": {"page": 1, "page_size": 20, "total": 1},
                },
                "errors": [],
            }
        }