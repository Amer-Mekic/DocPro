import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.line_item import LineItem
from app.models.validation_issue import ValidationIssue
from app.schemas.document import DocumentUploadResponse
from app.services.extraction import extract_document, extract_document_from_image
from app.services.ingestion import parse_file

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


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
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

            document.line_items.clear()
            for item in extracted.get("line_items", []):
                document.line_items.append(
                    LineItem(
                        description=item.get("description"),
                        quantity=item.get("quantity"),
                        unit_price=item.get("unit_price"),
                        line_total=item.get("line_total"),
                    )
                )

            document.status = "validated"
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

        return DocumentUploadResponse(
            id=document.id,
            status=document.status,
            file_path=document.file_path,
            created_at=document.created_at,
        )

    except HTTPException:
        raise
    except Exception as error:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {error}")