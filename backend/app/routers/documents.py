import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.document import Document
from app.models.line_item import LineItem
from app.models.validation_issue import ValidationIssue
from app.schemas.document import (
    DocumentPatchRequest,
    DocumentUploadResponse,
    DocumentResponse,
    DocumentEnvelope,
    DocumentListEnvelope,
    DocumentUploadEnvelope,
)
from app.services.extraction import extract_document, extract_document_from_image
from app.services.ingestion import parse_file
from app.services.validation import refresh_validation
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/documents", tags=["documents"])

UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def _json_safe(value):
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


def _load_line_items(document: Document, line_items: list[dict]) -> None:
    document.line_items.clear()
    for item in line_items:
        document.line_items.append(
            LineItem(
                description=item.get("description"),
                quantity=item.get("quantity"),
                unit_price=item.get("unit_price"),
                line_total=item.get("line_total"),
            )
        )


def _serialize_line_item(item: LineItem) -> dict:
    return {
        "id": item.id,
        "description": item.description,
        "quantity": float(item.quantity) if item.quantity is not None else None,
        "unit_price": float(item.unit_price) if item.unit_price is not None else None,
        "line_total": float(item.line_total) if item.line_total is not None else None,
    }


def _serialize_issue(issue: ValidationIssue) -> dict:
    return {
        "id": issue.id,
        "field_name": issue.field_name,
        "issue_type": issue.issue_type,
        "message": issue.message,
        "severity": issue.severity,
    }


def _serialize_document(doc: Document, full: bool = False) -> dict:
    base = {
        "id": doc.id,
        "status": doc.status,
        "doc_type": doc.doc_type,
        "supplier_name": doc.supplier_name,
        "document_number": doc.document_number,
        "issue_date": doc.issue_date.isoformat() if doc.issue_date else None,
        "due_date": doc.due_date.isoformat() if doc.due_date else None,
        "currency": doc.currency,
        "subtotal": float(doc.subtotal) if doc.subtotal is not None else None,
        "tax": float(doc.tax) if doc.tax is not None else None,
        "total": float(doc.total) if doc.total is not None else None,
        "file_path": doc.file_path,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }

    if full:
        base["raw_text"] = doc.raw_text
        base["line_items"] = [_serialize_line_item(i) for i in doc.line_items]
        base["validation_issues"] = [_serialize_issue(i) for i in doc.validation_issues]

    return base


@router.post(
    "/upload",
    response_model=DocumentUploadEnvelope,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "data": {"id": "00000000-0000-0000-0000-000000000000", "status": "uploaded", "file_path": "uploads/000.png", "created_at": "2026-05-15T12:00:00Z"},
                        "errors": [],
                    }
                }
            }
        }
    },
)
@limiter.limit("4/hour")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    file_extension = Path(file.filename).suffix.lstrip(".").lower()
    supported_extensions = {"pdf", "png", "jpg", "jpeg", "webp", "csv", "txt"}

    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {', '.join(supported_extensions)}",
        )

    doc_id = uuid.uuid4()
    filename = f"{doc_id}.{file_extension}"
    file_path = UPLOADS_DIR / filename

    try:
        content = await file.read()
        with open(file_path, "wb") as handle:
            handle.write(content)

        document = Document(
            id=doc_id,
            status="uploaded",
            file_path=str(file_path),
        )
        db.add(document)
        db.commit()

        try:
            if file_extension in IMAGE_EXTENSIONS:
                extracted = extract_document_from_image(str(file_path))
                document.raw_text = json.dumps(_json_safe(extracted), ensure_ascii=False)
            else:
                raw_text = parse_file(str(file_path), file_extension)
                document.raw_text = raw_text
                extracted = extract_document(raw_text)

            document.doc_type = extracted.get("doc_type")
            document.supplier_name = extracted.get("supplier_name")
            document.document_number = extracted.get("document_number")
            document.issue_date = extracted.get("issue_date")
            document.due_date = extracted.get("due_date")
            document.currency = extracted.get("currency")
            document.subtotal = extracted.get("subtotal")
            document.tax = extracted.get("tax")
            document.total = extracted.get("total")

            _load_line_items(document, extracted.get("line_items", []))
            refresh_validation(document, db)
            db.commit()

        except Exception as extraction_error:
            document.status = "needs_review"
            document.validation_issues.append(
                ValidationIssue(
                    field_name="raw_text",
                    issue_type="extraction_failed",
                    message=str(extraction_error),
                    severity="error",
                )
            )
            db.commit()

        return {"data": {"id": document.id, "status": document.status, "file_path": document.file_path, "created_at": document.created_at}, "errors": []}

    except HTTPException:
        raise
    except Exception as error:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {error}")


@router.patch("/{document_id}", response_model=DocumentEnvelope)
async def patch_document(
    document_id: uuid.UUID,
    payload: DocumentPatchRequest,
    db: Session = Depends(get_db),
 ) -> dict:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    update_data = payload.model_dump(exclude_unset=True)
    line_items = update_data.pop("line_items", None)

    for field_name, value in update_data.items():
        setattr(document, field_name, value)

    if line_items is not None:
        document.line_items.clear()
        for item in line_items:
            document.line_items.append(
                LineItem(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                )
            )

    refresh_validation(document, db)
    db.commit()
    db.refresh(document)
    return {"data": _serialize_document(document, full=True), "errors": []}


@router.post("/{document_id}/confirm", response_model=DocumentEnvelope)
async def confirm_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.validation_issues.clear()
    document.status = "validated"
    db.commit()
    db.refresh(document)
    return {"data": _serialize_document(document, full=True), "errors": []}


@router.post("/{document_id}/reject", response_model=DocumentEnvelope)
async def reject_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = "rejected"
    db.commit()
    db.refresh(document)
    return {"data": _serialize_document(document, full=True), "errors": []}


@router.get("/", response_model=DocumentListEnvelope)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict:
    query = db.query(Document)
    total = query.count()
    items = (
        query.order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    data = [
        {
            "id": item.id,
            "status": item.status,
            "doc_type": item.doc_type,
            "supplier_name": item.supplier_name,
            "document_number": item.document_number,
            "total": float(item.total) if item.total is not None else None,
            "currency": item.currency,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in items
    ]

    meta = {"page": page, "page_size": page_size, "total": total}
    return {"data": {"items": data, "meta": meta}, "errors": []}


@router.get("/{document_id}", response_model=DocumentEnvelope)
async def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"data": _serialize_document(document, full=True), "errors": []}


@router.get("/dashboard/summary")
async def dashboard_summary(db: Session = Depends(get_db)) -> dict:
    counts = db.query(Document.status, func.count()).group_by(Document.status).all()
    totals = db.query(Document.currency, func.sum(Document.total)).group_by(Document.currency).all()

    counts_map = {status: count for status, count in counts}
    totals_map = {currency: float(total) if total is not None else 0.0 for currency, total in totals}

    return {"data": {"counts": counts_map, "totals": totals_map}, "errors": []}


@router.post("/{document_id}/validate", response_model=DocumentEnvelope)
async def validate_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
 ) -> dict:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    refresh_validation(document, db)
    db.commit()
    db.refresh(document)
    return {"data": _serialize_document(document, full=True), "errors": []}
