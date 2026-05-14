import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(
        Enum("uploaded", "needs_review", "validated", "rejected", name="document_status", native_enum=False),
        nullable=False,
        default="uploaded",
    )
    doc_type: Mapped[str | None] = mapped_column(
        Enum("invoice", "purchase_order", name="document_type", native_enum=False),
        nullable=True,
    )
    supplier_name: Mapped[str | None] = mapped_column(String, nullable=True)
    document_number: Mapped[str | None] = mapped_column(String, nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str | None] = mapped_column(String, nullable=True)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    tax: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    total: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.timezone("utc", func.now()),
    )

    line_items: Mapped[list["LineItem"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    validation_issues: Mapped[list["ValidationIssue"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
