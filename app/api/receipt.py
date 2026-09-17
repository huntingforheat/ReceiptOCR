from fastapi import (
  APIRouter,
  File,
  HTTPException,
  UploadFile,
)

from app.infrastructure.azure_document import (
  AzureReceiptOcrAdapter,
)
from app.schemas.receipt import ReceiptOcrResponse
from app.services.receipt_service import ReceiptService


router = APIRouter(
  prefix="/ocr",
  tags=["Receipt OCR"]
)


ocr_adapter = AzureReceiptOcrAdapter()

receipt_service = ReceiptService(
  ocr_adapter=ocr_adapter
)

@router.post(
    "/receipt",
    response_model=ReceiptOcrResponse
)
def analyze_receipt(
    # File(...) 은 파일 업로드 파라미터인데 필수라고 생각하면 됨
    file: UploadFile = File(...)
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
    return receipt_service.analyze_receipt(file)

  except ValueError as e:
    raise HTTPException(
      status_code=422,
      detail=str(e)
    )