from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
  Date,
  DateTime,
  ForeignKey,
  Numeric,
  String,
  func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Trip(Base):
  __tablename__ = "trip"

  id: Mapped[int] = mapped_column(
    primary_key=True
  )

  name: Mapped[str] = mapped_column(
    String(200),
    nullable=False
  )

  country: Mapped[str] = mapped_column(
    String(100),
    nullable=False
  )

  start_date: Mapped[date | None] = mapped_column(
    Date,
    nullable=True
  )

  end_date: Mapped[date | None] = mapped_column(
    Date,
    nullable=True
  )

  base_currency: Mapped[str] = mapped_column(
    String(3),
    nullable=False,
    default="KRW"
  )

  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
  )

  receipts: Mapped[list["Receipt"]] = relationship(
    back_populates="trip",
    cascade="all, delete-orphan"
  )


class Receipt(Base):
    __tablename__ = "receipt"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trip.id"),
        nullable=False
    )

    original_filename: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    merchant_name: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True
    )

    transaction_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    total: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True
    )

    currency: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="receipts"
    )

    items: Mapped[list["ReceiptItem"]] = relationship(
        back_populates="receipt",
        cascade="all, delete-orphan"
    )


class ReceiptItem(Base):
  __tablename__ = "receipt_item"

  id: Mapped[int] = mapped_column(
    primary_key=True
  )

  receipt_id: Mapped[int] = mapped_column(
    ForeignKey("receipt.id"),
    nullable=False
  )

  name: Mapped[str | None] = mapped_column(
    String(500),
    nullable=True
  )

  quantity: Mapped[Decimal | None] = mapped_column(
    Numeric(15, 2),
    nullable=True
  )

  unit_price: Mapped[Decimal | None] = mapped_column(
    Numeric(15, 2),
    nullable=True
  )

  total_price: Mapped[Decimal | None] = mapped_column(
    Numeric(15, 2),
    nullable=True
  )

  category: Mapped[str | None] = mapped_column(
    String(50),
    nullable=True
  )

  receipt: Mapped["Receipt"] = relationship(
    back_populates="items"
  )

