import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentUploadResponse
from app.services.ingestion import parse_file

router = APIRouter(prefix="/documents", tags=["documents"])

# Get uploads directory
UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """
    Upload and parse a document file.

    Accepted formats: PDF, PNG, JPG, JPEG, WEBP, CSV, TXT
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")

    file_extension = Path(file.filename).suffix.lstrip(".").lower()
    supported_extensions = {"pdf", "png", "jpg", "jpeg", "webp", "csv", "txt"}

    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {', '.join(supported_extensions)}",
        )

    try:
        # Generate unique filename
        doc_id = uuid.uuid4()
        filename = f"{doc_id}.{file_extension}"
        file_path = UPLOADS_DIR / filename

        # Save file to disk
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Create document record with initial status
        document = Document(
            id=doc_id,
            status="uploaded",
            file_path=str(file_path),
        )
        db.add(document)
        db.commit()

        # Parse file and extract text
        try:
            raw_text = parse_file(str(file_path), file_extension)
            document.raw_text = raw_text
            db.commit()
        except Exception as parse_error:
            # If parsing fails, remove the file but keep the document record
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse file: {str(parse_error)}",
            )

        return DocumentUploadResponse(
            id=document.id,
            status=document.status,
            file_path=document.file_path,
            created_at=document.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if something goes wrong
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )