from fastapi import FastAPI

from app.api.receipt import router as receipt_router


app = FastAPI(
  title="Travel Receipt API",
  version="0.1.0"
)


app.include_router(receipt_router)


@app.get("/")
def health_check():
  return {
    "message": "Travel Receipt API"
  }