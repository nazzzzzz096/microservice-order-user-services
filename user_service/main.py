from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import models
import schemas
import crud
import database
from logging_config import setup_logger
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
import time
import uuid
from sqlalchemy import text
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os

logger = setup_logger("user_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service starting up...")
    models.Base.metadata.create_all(bind=database.engine)
    yield
    logger.info("Service shutting down")

app = FastAPI(title="User Service", lifespan=lifespan)
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

@app.post("/users/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    logger.info("User registered", extra={"user_id": db_user.id})
    return {"id": db_user.id, "email": db_user.email}

@app.post("/verify-token")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {"id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")