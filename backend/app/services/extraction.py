import base64
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.services.llm_client import get_client, get_llm_model


class ExtractedLineItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    description: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    line_total: Decimal | None = None

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("quantity", "unit_price", "line_total", mode="before")
    @classmethod
    def normalize_decimal(cls, value: object) -> object:
        if value in (None, "", "null"):
            return None
        if isinstance(value, str):
            return value.replace(",", "").strip()
        return value


class ExtractedDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")

    doc_type: Literal["invoice", "purchase_order"] | None = None
    supplier_name: str | None = None
    document_number: str | None = None
    issue_date: date | None = None
    due_date: date | None = None
    currency: str | None = None
    line_items: list[ExtractedLineItem] = Field(default_factory=list)
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    total: Decimal | None = None

    @field_validator("supplier_name", "document_number", "currency", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("issue_date", "due_date", mode="before")
    @classmethod
    def parse_ddmmyyyy(cls, value: object) -> date | None:
        if value in (None, "", "null"):
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return datetime.strptime(value.strip(), "%d-%m-%Y").date()
        raise ValueError("Date must be in DD-MM-YYYY format")

    @field_validator("subtotal", "tax", "total", mode="before")
    @classmethod
    def normalize_decimal(cls, value: object) -> object:
        if value in (None, "", "null"):
            return None
        if isinstance(value, str):
            return value.replace(",", "").strip()
        return value
    
    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_field(cls, value: object) -> str | None:
        return normalize_currency(value)


def _parse_llm_json_response(content: str) -> dict:
    if not content or not content.strip():
        raise ValueError("LLM returned empty response")

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON from LLM: {exc}") from exc

    try:
        validated = ExtractedDocument.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Extraction validation failed: {exc}") from exc

    return validated.model_dump(mode="python")


def extract_document(raw_text: str) -> dict:
    system_prompt = (
        "You are an information extraction system. "
        "Return ONLY valid JSON. No prose. No markdown fences. "
        "Extract exactly these fields: doc_type, supplier_name, document_number, "
        "issue_date, due_date, currency, line_items, subtotal, tax, total. "
        "doc_type must be invoice or purchase_order. "
        "issue_date and due_date must be DD-MM-YYYY. "
        "line_items must be an array of objects with description, quantity, unit_price, line_total. "
        "If a value is missing, use null."
    )

    response = get_client().chat.completions.create(
        model=get_llm_model(),
        max_tokens=1000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text},
        ],
    )

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise ValueError("LLM returned a non-text response")

    return _parse_llm_json_response(content)

def normalize_currency(value: object) -> str | None:
    if value is None:
        return None

    text = str(value).strip().upper()
    if not text:
        return None

    symbol_map = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "¥": "JPY",
    }

    if text in symbol_map:
        return symbol_map[text]

    return text

def extract_document_from_image(file_path: str) -> dict:
    suffix = Path(file_path).suffix.lower().lstrip(".")
    media_type_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }
    media_type = media_type_map.get(suffix, "image/png")

    with open(file_path, "rb") as handle:
        image_data = base64.b64encode(handle.read()).decode("utf-8")

    system_prompt = """
        You are extracting structured data from a business document image.

        This document contains a table with line items. You MUST extract every row from that table.
        Look carefully at the full image including any colored or styled table sections.

        Return ONLY a valid JSON object with this exact structure, no preamble, no markdown:
        {
        "doc_type": "invoice" or "purchase_order",
        "supplier_name": "...",
        "document_number": "...",
        "issue_date": "DD-MM-YYYY or null",
        "due_date": "DD-MM-YYYY or null",
        "currency": "USD/EUR/etc",
        "subtotal": 0.00,
        "tax": 0.00,
        "total": 0.00,
        "line_items": [
            {
            "description": "...",
            "quantity": 0,
            "unit_price": 0.00,
            "line_total": 0.00
            }
        ]
        }

        Rules:
        - line_items must contain every row from the table, even if there are many rows
        - Extract numeric values as numbers, not strings (no currency symbols)
        - If a field is not found, use null
        - Do not skip table rows
        - "currency" must be an ISO 4217 code like USD, EUR, GBP. If the document shows only a symbol, convert it to the matching code.
    """

    response = get_client().chat.completions.create(
        model=get_llm_model(),
        max_tokens=1000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the document directly from this image. Preserve tables and line items in JSON.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}",
                        },
                    },
                ],
            },
        ],
    )

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise ValueError("LLM returned a non-text response")

    return _parse_llm_json_response(content)