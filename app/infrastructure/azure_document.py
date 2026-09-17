import os
# Python 표준 라이브러리
from typing import BinaryIO

# 외부 라이브러리
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# 내 프로젝트
from app.schemas.receipt import (
  ReceiptItemResponse,
  ReceiptOcrResponse
)


load_dotenv()


class AzureReceiptOcrAdapter:

  def __init__(self):
    endpoint = os.getenv("DI_ENDPOINT")
    key = os.getenv("DI_KEY")

    if not endpoint:
      raise RuntimeError(
        "DI_ENDPOINT 환경변수가 없습니다."
      )

    if not key:
      raise RuntimeError(
        "DI_KEY 환경변수가 없습니다."
      )

    self.client = DocumentIntelligenceClient(
      endpoint=endpoint,
      credential=AzureKeyCredential(key)
    )

  def analyze(
      self,
      filename: str,
      file: BinaryIO
  ) -> ReceiptOcrResponse:

    poller = self.client.begin_analyze_document(
        "prebuilt-receipt",
        body=file,
        content_type="application/octet-stream"
    )

    result = poller.result()

    if not result.documents:
      raise ValueError(
        "영수증을 인식하지 못했습니다."
      )

    receipt = result.documents[0]
    fields = receipt.fields or {}

    merchant_field = fields.get("MerchantName")
    date_field = fields.get("TransactionDate")
    total_field = fields.get("Total")

    merchant_name = (
      merchant_field.value_string
      if merchant_field
      else None
    )

    transaction_date = (
      date_field.value_date
      if date_field
      else None
    )

    total, currency = self._get_currency(
      total_field
    )

    items = self._parse_items(fields)

    return ReceiptOcrResponse(
      filename=filename,
      merchant_name=merchant_name,
      transaction_date=transaction_date,
      total=total,
      currency=currency,
      items=items
    )

  # 메서드 이름 앞에 _ 하나를 붙이는 건 파이썬에서 "이 메서드는 내부용으로 쓰는 메서드입니다" 라는 관례
  # 호출할 수 있게 막아놓은 건 아니지만, 내부 구현용이니깐 외부에서는 가급적 직접 사용하지 말라는
  # 개발자 간 약속에 가까움
  # 자바로 치면 private와 같음
  def _get_currency(self, field):

    if field is None:
      return None, None

    if field.value_currency is not None:
      currency = field.value_currency

      return (
        currency.amount,
        currency.currency_code
      )

    if field.value_number is not None:
      return field.value_number, None

    return None, None

  def _get_number(self, field):

    if field is None:
      return None

    if field.value_number is not None:
      return field.value_number

    if field.value_currency is not None:
      return field.value_currency.amount

    return None

  def _parse_items(
      self,
      fields
  ) -> list[ReceiptOcrResponse]:

    items_field = fields.get("Items")

    if (
      not items_field
      or not items_field.value_array
    ):

      return []

    items = []

    for item in items_field.value_array:

      values = item.value_object or {}

      description = values.get("Description")
      quantity = values.get("Quantity")
      price = values.get("Price")
      total_price = values.get("TotalPrice")

      items.append(
        ReceiptItemResponse(
          name=(
            description.value_string
            if description
            else None
          ),
          quantity=self._get_number(
            quantity
          ),
          unit_price=self._get_number(
            price
          ),
          total_price=self._get_number(
            total_price
          )
        )
      )

    return items

    