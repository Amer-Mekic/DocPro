from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.line_item import LineItem
from app.models.validation_issue import ValidationIssue


def _decimal(value: object) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _quantize(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _issue(document: Document, field_name: str, issue_type: str, message: str, severity: str) -> ValidationIssue:
    return ValidationIssue(
        document_id=document.id,
        field_name=field_name,
        issue_type=issue_type,
        message=message,
        severity=severity,
    )


def validate_required_fields(document: Document, line_items: list[LineItem]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    required_fields = [
        ("supplier_name", document.supplier_name),
        ("document_number", document.document_number),
        ("issue_date", document.issue_date),
        ("total", document.total),
        ("currency", document.currency),
    ]

    for field_name, value in required_fields:
        if value is None or (isinstance(value, str) and not value.strip()):
            issues.append(
                _issue(
                    document,
                    field_name=field_name,
                    issue_type="required_field_missing",
                    message=f"{field_name} is required",
                    severity="error",
                )
            )

    return issues


def validate_line_item_calculations(document: Document, line_items: list[LineItem]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for index, item in enumerate(line_items, start=1):
        quantity = _decimal(item.quantity)
        unit_price = _decimal(item.unit_price)
        line_total = _decimal(item.line_total)

        if quantity is None or unit_price is None or line_total is None:
            issues.append(
                _issue(
                    document,
                    field_name="line_items",
                    issue_type="line_item_calculation_failed",
                    message=f"Line item {index} is missing quantity, unit_price, or line_total",
                    severity="error",
                )
            )
            continue

        expected = _quantize(quantity * unit_price)
        actual = _quantize(line_total)

        if expected != actual:
            issues.append(
                _issue(
                    document,
                    field_name="line_items",
                    issue_type="line_item_calculation_failed",
                    message=f"Line item {index} does not match quantity × unit_price",
                    severity="error",
                )
            )

    return issues


def validate_subtotal_matches_line_items(document: Document, line_items: list[LineItem]) -> list[ValidationIssue]:
    subtotal = _decimal(document.subtotal)
    if subtotal is None:
        return []

    line_totals = []
    for item in line_items:
        line_total = _decimal(item.line_total)
        if line_total is not None:
            line_totals.append(line_total)

    expected = _quantize(sum(line_totals, Decimal("0")))
    actual = _quantize(subtotal)

    if expected != actual:
        return [
            _issue(
                document,
                field_name="subtotal",
                issue_type="subtotal_mismatch",
                message="Subtotal does not match the sum of line item totals",
                severity="error",
            )
        ]

    return []


def validate_total_matches_subtotal_and_tax(document: Document, line_items: list[LineItem]) -> list[ValidationIssue]:
    subtotal = _decimal(document.subtotal)
    tax = _decimal(document.tax)
    total = _decimal(document.total)

    if subtotal is None or tax is None or total is None:
        return []

    expected = _quantize(subtotal + tax)
    actual = _quantize(total)

    if expected != actual:
        return [
            _issue(
                document,
                field_name="total",
                issue_type="total_mismatch",
                message="Total does not match subtotal plus tax",
                severity="error",
            )
        ]

    return []


def validate_dates(document: Document, line_items: list[LineItem]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if document.issue_date and document.due_date and document.issue_date >= document.due_date:
        issues.append(
            _issue(
                document,
                field_name="issue_date",
                issue_type="date_order_warning",
                message="issue_date should be before due_date",
                severity="warning",
            )
        )

    return issues


def validate_duplicate_document_number(document: Document, db: Session) -> list[ValidationIssue]:
    if not document.document_number:
        return []

    duplicate_exists = (
        db.query(Document.id)
        .filter(
            Document.document_number == document.document_number,
            Document.id != document.id,
        )
        .first()
    )

    if duplicate_exists:
        return [
            _issue(
                document,
                field_name="document_number",
                issue_type="duplicate_document_number",
                message="document_number already exists for another document",
                severity="error",
            )
        ]

    return []


def run_validation_rules(document: Document, db: Session) -> list[ValidationIssue]:
    line_items = list(document.line_items)
    issues: list[ValidationIssue] = []

    issues.extend(validate_required_fields(document, line_items))
    issues.extend(validate_line_item_calculations(document, line_items))
    issues.extend(validate_subtotal_matches_line_items(document, line_items))
    issues.extend(validate_total_matches_subtotal_and_tax(document, line_items))
    issues.extend(validate_dates(document, line_items))
    issues.extend(validate_duplicate_document_number(document, db))

    return issues


def refresh_validation(document: Document, db: Session) -> list[ValidationIssue]:
    issues = run_validation_rules(document, db)

    document.validation_issues.clear()
    document.validation_issues.extend(issues)
    document.status = "validated" if not issues else "needs_review"

    db.flush()
    return issues