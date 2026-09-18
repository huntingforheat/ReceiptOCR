from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import requests


@dataclass
class ExchangeRateResult:
  rate: Decimal
  rate_date: date


class ExchangeRateAdapter:

  BASE_URL = "https://api.frankfurter.dev/v2"

  def get_rate(
      self,
      base_currency: str,
      target_currency: str,
      transaction_date: date | None = None
  ) -> ExchangeRateResult:

    base_currency = base_currency.upper()
    target_currency = target_currency.upper()

    # 같은 화폐면 환율 조회 필요 없음
    if base_currency == target_currency:

      return ExchangeRateResult(
        rate=Decimal("1"),
        rate_date=transaction_date or date.today()
      )

    url = (
      f"{self.BASE_URL}"
      f"/rate/{base_currency}/{target_currency}"
    )

    params = {}

    if transaction_date:
      params["date"] = transaction_date.isoformat()

    response = requests.get(
      url,
      params=params,
      timeout=10
    )

    response.raise_for_status()

    # float 오차를 줄이기 위해
    # JSON 문자열 값을 Decimal로 변환
    data = response.json(
      parse_float=Decimal
    )

    return ExchangeRateResult(
      rate=Decimal(str(data["rate"])),
      rate_date=date.fromisoformat(
        data["date"]
      )
    )