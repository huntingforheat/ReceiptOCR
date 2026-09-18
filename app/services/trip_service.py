from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.entities import (
  Receipt,
  Trip,
)
from app.schemas.trip import (
  TripCreate,
  TripSummaryResponse,
)


class TripService:

  def create(
      self,
      db: Session,
      request: TripCreate
  ) -> Trip:

    trip = Trip(
      name=request.name,
      country=request.country,
      start_date=request.start_date,
      end_date=request.end_date,
      base_currency=request.base_currency
    )

    db.add(trip)
    db.commit()
    db.refresh(trip)

    return trip

  def find_all(
      self,
      db: Session
  ) -> list[Trip]:

    stmt = (
      select(Trip)
      .order_by(Trip.id.desc())
    )

    return list(
      db.scalars(stmt).all()
    )

  def get_summary(
      self,
      db: Session,
      trip_id: int
  ) -> TripSummaryResponse:

    trip = db.get(
      Trip,
      trip_id
    )

    if trip is None:
      raise LookupError(
        "여행 정보를 찾을 수 없습니다."
      )

    stmt = (
      select(
        func.count(Receipt.id),
        func.coalesce(
          func.sum(
            Receipt.converted_total
          ),
          0
        )
      )
      .where(
        Receipt.trip_id == trip_id
      )
    )

    receipt_count, total_spent = (
      db.execute(stmt).one()
    )

    return TripSummaryResponse(
      trip_id=trip_id,
      trip_name=trip.name,
      base_currency=trip.base_currency,
      receipt_count=receipt_count,
      total_spent=Decimal(
        str(total_spent)
      )
    )