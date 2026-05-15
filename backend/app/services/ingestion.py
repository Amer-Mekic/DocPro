import base64
import json
import os

import pandas as pd
import pdfplumber

from app.services.llm_client import get_client, get_llm_model
from app.services.extraction import extract_document_from_image


def parse_file(file_path: str, extension: str) -> str:
    """
    Parse a document file and extract text content.

    Args:
        file_path: Absolute path to the file to parse
        extension: File extension (pdf, png, jpg, jpeg, webp, csv, txt)

    Returns:
        Plain string containing extracted text

    Raises:
        ValueError: If extension is not supported
        FileNotFoundError: If file does not exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = extension.lower()

    if extension == "pdf":
        return _parse_pdf(file_path)
    elif extension in ("png", "jpg", "jpeg", "webp"):
        return _parse_image(file_path)
    elif extension == "csv":
        return _parse_csv(file_path)
    elif extension == "txt":
        return _parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {extension}")


def _parse_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    text_pages = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)

    return "\n\n".join(text_pages)


def _parse_image(file_path: str) -> str:
    extracted = extract_document_from_image(file_path)
    return json.dumps(extracted, ensure_ascii=False)

def _parse_csv(file_path: str) -> str:
    """Convert CSV to readable key-value text format."""
    df = pd.read_csv(file_path)

    lines = []
    for idx, row in df.iterrows():
        lines.append(f"--- Row {idx + 1} ---")
        for col, value in row.items():
            # Handle NaN values
            if pd.isna(value):
                lines.append(f"{col}: (empty)")
            else:
                lines.append(f"{col}: {value}")
        lines.append("")

    return "\n".join(lines).strip()


def _parse_txt(file_path: str) -> str:
    """Read plain text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()
