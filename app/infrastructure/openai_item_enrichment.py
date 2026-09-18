import os

from openai import OpenAI
from dotenv import load_dotenv

from app.schemas.enrichment import (
  ItemEnrichmentResult,
)


load_dotenv()


class OpenAIItemEnrichmentAdapter:

  def __init__(self):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
      raise RuntimeError(
        "OPENAI_API_KEY 환경변수가 없습니다."
      )

    self.model = os.getenv(
      "OPENAI_MODEL",
      "gpt-5.6-luna"
    )

    self.client = OpenAI(
      api_key=api_key
    )

  def enrich(
      self,
      items: list[tuple[int, str]],
      merchant_name: str | None = None,
      country: str | None = None
  ) -> ItemEnrichmentResult:

    item_text = "\n".join(
      f"{index}: {name}"
      for index, name in items
    )

    context = (
      f"가맹점: {merchant_name or '알 수 없음'}\n"
      f"국가: {country or '알 수 없음'}"
    )

    response = self.client.responses.parse(
      model=self.model,

      input=[
        {
          "role": "system",
          "content": (
            "당신은 해외여행 영수증 품목을 "
            "정리하는 시스템입니다.\n\n"

            "각 품목에 대해 다음 작업을 수행하세요.\n"
            "1. 원문을 자연스러운 한국어 품목명으로 번역\n"
            "2. 지정된 카테고리 중 하나로 분류\n\n"

            "카테고리 기준:\n"
            "- FOOD: 일반 음식, 식사, 식료품\n"
            "- CAFE: 커피, 음료, 카페 관련\n"
            "- TRANSPORT: 지하철, 버스, 택시, 기차 등\n"
            "- SHOPPING: 의류, 잡화, 기념품, 생활용품\n"
            "- HOTEL: 호텔, 숙박\n"\
            "- ENTERTAINMENT: 관광지, 공연, 놀이시설\n"
            "- ETC: 어디에도 명확히 해당하지 않는 경우\n\n"

            "입력 index는 절대로 변경하지 마세요."
          )
        },
        {
          "role": "user",
          "content": (
            f"{context}\n\n"
            f"품목:\n{item_text}"
          )
        }
      ],

      text_format=ItemEnrichmentResult
    )

    result = response.output_parsed

    if result is None:
      raise ValueError(
        "AI 품목 분석 결과를 가져오지 못했습니다."
      )

    return result