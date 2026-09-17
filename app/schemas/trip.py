from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TripCreate(BaseModel):
  name: str
  country: str

  start_date: date | None = None
  end_date: date | None = None

  base_currency: str = "KRW"


class TripResponse(BaseModel):
  model_config = ConfigDict(
    from_attributes=True
  )

  id: int
  name: str
  country: str

  start_date: date | None
  end_date: date | None

  base_currency: str
  created_at: datetime