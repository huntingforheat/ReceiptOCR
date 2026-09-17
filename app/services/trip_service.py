from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Trip
from app.schemas.trip import TripCreate


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