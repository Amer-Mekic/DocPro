"""Initial document processing models.

Revision ID: 20260513_0001
Revises:
Create Date: 2026-05-13
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260513_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "uploaded",
                "needs_review",
                "validated",
                "rejected",
                name="document_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "doc_type",
            sa.Enum("invoice", "purchase_order", name="document_type", native_enum=False),
            nullable=True,
        ),
        sa.Column("supplier_name", sa.String(), nullable=True),
        sa.Column("document_number", sa.String(), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(), nullable=True),
        sa.Column("subtotal", sa.Numeric(), nullable=True),
        sa.Column("tax", sa.Numeric(), nullable=True),
        sa.Column("total", sa.Numeric(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', NOW())"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "line_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("quantity", sa.Numeric(), nullable=True),
        sa.Column("unit_price", sa.Numeric(), nullable=True),
        sa.Column("line_total", sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "validation_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_name", sa.String(), nullable=False),
        sa.Column("issue_type", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("error", "warning", name="validation_severity", native_enum=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("validation_issues")
    op.drop_table("line_items")
    op.drop_table("documents")
