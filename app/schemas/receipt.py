from datetime import date

from pydantic import BaseModel, Field


class ReceiptItemResponse(BaseModel):
  # String 또는 null 가능
  name: str | None = None
  quantity: float | None = None
  unit_price: float | None = None
  total_price: float | None = None


class ReceiptOcrResponse(BaseModel):
  # String 필수
  filename: str
  merchant_name: str | None = None
  transaction_date: date | None = None
  total: float | None = None
  currency: str | None = None

  items: list[ReceiptItemResponse] = Field(
    default_factory=list 
  )
