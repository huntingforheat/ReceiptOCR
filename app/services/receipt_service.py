from fastapi import UploadFile

from app.infrastructure.azure_document import (
  AzureReceiptOcrAdapter,
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