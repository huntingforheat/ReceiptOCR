from fastapi import FastAPI

from app.api.receipt import router as receipt_router
from app.api.trip import router as trip_router


app = FastAPI(
  title="Travel Receipt API",
  version="0.2.0"
)


app.include_router(receipt_router)

app.include_router(trip_router)


@app.get("/")
def health_check():
  return {
    "message": "Travel Receipt API"
  }