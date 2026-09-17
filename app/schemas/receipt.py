from datetime import date

from pydantic import BaseModel, ConfigDict, Field


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


class ReceiptItemSavedResponse(BaseModel):
  model_config = ConfigDict(
    from_attributes=True
  )

  id: int
  name: str | None
  quantity: float | None
  unit_price: float | None
  total_price: float | None
  category: str | None


class ReceiptSavedResponse(BaseModel):
  model_config = ConfigDict(
    from_attributes=True
  )

  id: int
  trip_id: int

  original_filename: str | None
  merchant_name: str | None
  transaction_date: date | None

  total: float | None
  currency: str | None

  items: list[ReceiptItemSavedResponse] = Field(
    default_factory=list
  )
