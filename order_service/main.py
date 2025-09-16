from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import models
import schemas
import crud
import database
from logging_config import setup_logger
from services import validate_current_user
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
import time
import uuid
from sqlalchemy import text

logger = setup_logger("order_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service starting up...")
    models.Base.metadata.create_all(bind=database.engine)
    yield
    logger.info("Service shutting down")

app = FastAPI(title="Order Service", lifespan=lifespan)
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

@app.get("/health")
def health_check(db: Session = Depends(database.get_db)):
    try:
        db.execute(text("SELECT 1"))  # Changed to use text()
        logger.info("Health check: DB connected")
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        logger.error("Health check: DB failed", extra={"error": str(e)})
        raise HTTPException(status_code=503, detail="DB unavailable")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    user_id = "unknown"
    logger.info(
        f"Incoming request: {request.method} {request.url}",
        extra={"request_id": request_id, "user_id": user_id}
    )

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        f"Completed {request.method} {request.url} status={response.status_code}",
        extra={"request_id": request_id, "user_id": user_id, "duration": round(duration, 2)}
    )
    return response

@app.post("/orders/")
async def create_order_endpoint(order: schemas.OrderCreate, db: Session = Depends(database.get_db)):
    try:
        user_data = await validate_current_user("dummy_token")  # Placeholder; replace with actual token logic
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid user")
        db_order = crud.create_order(db, order, user_data.get("id", 1))  # Default user_id=1 for testing
        logger.info("Order created", extra={"order_id": db_order.id})
        return db_order
    except Exception as e:
        logger.error("Order creation failed", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))