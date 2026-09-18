from decimal import Decimal

from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.infrastructure.azure_document import (
  AzureReceiptOcrAdapter,
)
from app.infrastructure.exchange_rate import (
  ExchangeRateAdapter,
)
from app.models.entities import (
  Receipt,
  ReceiptItem,
  Trip
)
from app.schemas.receipt import ReceiptOcrResponse
from app.services.item_enrichment_service import (
  ItemEnrichmentService,
)


class ReceiptService:

  def __init__(
    self,
    ocr_adapter: AzureReceiptOcrAdapter,
    exchange_rate_adapter=None,
    item_enrichment_service=None
  ):
    self.ocr_adapter = ocr_adapter
    self.exchange_rate_adapter = exchange_rate_adapter
    self.item_enrichment_service = item_enrichment_service

  def analyze_receipt(
    self,
    file: UploadFile
  ) -> ReceiptOcrResponse:

    return self.ocr_adapter.analyze(
      filename=file.filename or "unknown",
      file=file.file
    )

  def analyze_and_save(
      self,
      db: Session,
      trip_id: int,
      file: UploadFile
  ) -> Receipt:

    trip = db.get(
      Trip,
      trip_id
    )

    if trip is None:
      raise LookupError(
        "여행 정보를 찾을 수 없습니다."
      )

    # -----------------
    # OCR
    # -----------------

    ocr_result = self.analyze_receipt(file)

    exchange_rate = None
    converted_total = None
    rate_date = None

    # -----------------
    # 환율 계산
    # -----------------

    if (
      ocr_result.total is not None
      and ocr_result.currency is not None
    ):

      rate_result = (
        self.exchange_rate_adapter.get_rate(
          base_currency=ocr_result.currency,
          target_currency=trip.base_currency,
          transaction_date=ocr_result.transaction_date
        )
      )

      exchange_rate = rate_result.rate
      rate_date = rate_result.rate_date

      converted_total = (
        Decimal(str(ocr_result.total))
        * exchange_rate
      )

      converted_total = (
        converted_total.quantize(
          Decimal("0.01")
        )
      )

    enriched_items = {}

    if self.item_enrichment_service:

      enriched_items = (
        self.item_enrichment_service.enrich(
          items=ocr_result.items,

          merchant_name=(
            ocr_result.merchant_name
          ),

          country=trip.country
        )
      )

    # -----------------
    # Receipt 생성
    # -----------------

    receipt = Receipt(
      trip_id=trip_id,
      original_filename=ocr_result.filename,
      merchant_name=ocr_result.merchant_name,
      transaction_date=ocr_result.transaction_date,
      total=self._decimal(
        ocr_result.total
      ),
      currency=ocr_result.currency,
      exchange_rate=exchange_rate,
      converted_total=converted_total,
      rate_date=rate_date
    )

    # ------------------
    # Receipt Item
    # ------------------

    for index, item in enumerate(
      ocr_result.items
    ):

      enriched = enriched_items.get(
        index
      )

      translated_name = (
        enriched.translated_name
        if enriched
        else item.name
      )

      category = (
        enriched.category.value
        if enriched
        else "ETC"
      )

      receipt.items.append(
        ReceiptItem(
          name=item.name,

          translated_name=(
            translated_name
          ),

          quantity=self._decimal(
            item.quantity
          ),

          unit_price=self._decimal(
            item.unit_price
          ),

          total_price=self._decimal(
            item.total_price
          ),

          category=category
        )
      )

    db.add(receipt)

    db.commit()

    db.refresh(receipt)

    return receipt

  def find_by_trip(
      self,
      db: Session,
      trip_id: int
  ) -> list[Receipt]:

    stmt = (
      select(Receipt)
      .where(
        Receipt.trip_id == trip_id
      )
      .order_by(
        Receipt.transaction_date.desc(),
        Receipt.id.desc()
      )
    )

    return list(
      db.scalars(stmt).all()
    )

  def _decimal(
      self,
      value
  ) -> Decimal | None:

    if value is None:
      return None

    return Decimal(str(value))
  