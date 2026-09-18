from fastapi import (
  APIRouter,
  Depends,
  File,
  HTTPException,
  UploadFile,
  status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.trip import (
  TripCreate,
  TripResponse,
  TripSummaryResponse,
)
from app.services.trip_service import TripService
from app.infrastructure.azure_document import (
  AzureReceiptOcrAdapter,
)
from app.infrastructure.exchange_rate import (
  ExchangeRateAdapter,
)
from app.infrastructure.openai_item_enrichment import (
  OpenAIItemEnrichmentAdapter,
)
from app.schemas.receipt import ReceiptSavedResponse
from app.services.receipt_service import ReceiptService
from app.services.item_enrichment_service import (
  ItemEnrichmentService,
)


router = APIRouter(
  prefix="/trips",
  tags=["Trips"]
)


trip_service = TripService()


ocr_adapter = AzureReceiptOcrAdapter()

exchange_rate_adapter = ExchangeRateAdapter()

openai_adapter = OpenAIItemEnrichmentAdapter()

item_enrichment_service = (
  ItemEnrichmentService(
    adapter=openai_adapter
  )
)


receipt_service = ReceiptService(
  ocr_adapter=ocr_adapter,
  exchange_rate_adapter=exchange_rate_adapter,
  item_enrichment_service=item_enrichment_service
)


@router.post(
    "",
    ## 응답 객체 지정할때 response_model 사용
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED
)
def create_trip(
    request: TripCreate,
    db: Session = Depends(get_db)
):
  return trip_service.create(
    db,
    request
  )


@router.get(
    "",
    response_model=list[TripResponse]
)
def get_trips(
    db: Session = Depends(get_db)
):
  return trip_service.find_all(db)


@router.post(
    "/{trip_id}/receipts",
    response_model=ReceiptSavedResponse,
    status_code=status.HTTP_201_CREATED
)
def upload_trip_receipt(
    trip_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

  if (
    not file.content_type
    or not file.content_type.startswith("image/")
  ):
    raise HTTPException(
      status_code=400,
      detail="이미지 파일만 업로드할 수 있습니다."
    )

  try:

    return receipt_service.analyze_and_save(
      db=db,
      trip_id=trip_id,
      file=file
    )

  except LookupError as e:

    raise HTTPException(
      status_code=404,
      detail=str(e)
    )

  except ValueError as e:

    raise HTTPException(
      status_code=422,
      detail=str(e)
    )


@router.get(
    "/{trip_id}/receipts",
    response_model=list[ReceiptSavedResponse]
)
def get_trip_receipts(
    trip_id: int,
    db: Session = Depends(get_db)
):

  return receipt_service.find_by_trip(
    db=db,
    trip_id=trip_id
  )

@router.get(
    "/{trip_id}/summary",
    response_model=TripSummaryResponse
)
def get_trip_summary(
    trip_id: int,
    db: Session = Depends(get_db)
):

  try:

    return trip_service.get_summary(
      db,
      trip_id
    )

  except LookupError as e:

    raise HTTPException(
      status_code=404,
      detail=str(e)
    )