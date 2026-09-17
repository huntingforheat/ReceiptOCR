from decimal import Decimal

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.infrastructure.azure_document import (
  AzureReceiptOcrAdapter,
)
from app.models.entities import (
  Receipt,
  ReceiptItem,
  Trip
)
from app.schemas.receipt import ReceiptOcrResponse


class ReceiptService:


  def __init__(
    self,
    ocr_adapter: AzureReceiptOcrAdapter
  ):
    self.ocr_adapter = ocr_adapter

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

    ocr_result = self.analyze_receipt(
      file
    )

    receipt = Receipt(
      trip_id=trip_id,
      original_filename=ocr_result.filename,
      merchant_name=ocr_result.merchant_name,
      transaction_date=ocr_result.transaction_date,
      total=self._decimal(
        ocr_result.total
      ),
      currency=ocr_result.currency
    )

    for item in ocr_result.items:

      receipt.items.append(
        ReceiptItem(
          name=item.name,
          quantity=self._decimal(
            item.quantity
          ),
          unit_price=self._decimal(
            item.unit_price
          ),
          total_price=self._decimal(
            item.total_price
          )
        )
      )

    db.add(receipt)

    db.commit()

    db.refresh(receipt)

    return receipt

  def _decimal(
      self,
      value
  ) -> Decimal | None:

    if value is None:
      return None

    return Decimal(str(value))
  