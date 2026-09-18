from enum import Enum

from pydantic import BaseModel


class ReceiptCategory(str, Enum):
  FOOD = "FOOD"
  CAFE = "CAFE"
  TRANSPORT = "TRANSPORT"
  SHOPPING = "SHOPPING"
  HOTEL = "HOTEL"
  ENTERTAINMENT = "ENTERTAINMENT"
  ETC = "ETC"


class EnrichedItem(BaseModel):
  index: int
  translated_name: str
  category: ReceiptCategory


class ItemEnrichmentResult(BaseModel):
  items: list[EnrichedItem]