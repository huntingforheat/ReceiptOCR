import logging

from app.infrastructure.openai_item_enrichment import (
  OpenAIItemEnrichmentAdapter,
)
from app.schemas.enrichment import (
  EnrichedItem,
  ReceiptCategory,
)
from app.schemas.receipt import ReceiptItemResponse


logger = logging.getLogger(__name__)


class ItemEnrichmentService:

  def __init__(
      self,
      adapter: OpenAIItemEnrichmentAdapter
  ):
    self.adapter = adapter

  def enrich(
      self,
      items: list[ReceiptItemResponse],
      merchant_name: str | None,
      country: str | None
  ) -> dict[int, EnrichedItem]:

    candidates = []

    for index, item in enumerate(items):

      if not item.name:
        continue

      candidates.append(
        (
          index,
          item.name
        )
      )

    if not candidates:
      return {}

    try:

      result = self.adapter.enrich(
        items=candidates,
        merchant_name=merchant_name,
        country=country
      )

      return {
        item.index: item
        for item in result.items
      }

    except Exception:

      logger.exception(
        "품목 AI 분석에 실패했습니다."
      )

      return {}
    