import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import BaseResponse
from app.routes.analysis import router as analysis_router
from app.routes.signals import router as signals_router

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plantpulse.api")

API_PREFIX = "/api/v1"

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://plant-pulse-jmsp.vercel.app",
]

app = FastAPI(title="PlantPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

app.include_router(signals_router, prefix=API_PREFIX)
app.include_router(analysis_router, prefix=API_PREFIX)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code >= 500:
        logger.error("Erro HTTP interno em %s", request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail)},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else None
    message = "Parametros de entrada invalidos."

    if first_error and first_error.get("loc", [])[-1] == "limit":
        message = "limit deve ser maior que zero e menor ou igual a 1000."
    elif first_error and first_error.get("loc", [])[-1] == "sensor_id":
        message = "sensor_id deve ter pelo menos 1 caractere."

    logger.warning("Falha de validacao em %s: %s", request.url.path, message)

    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": message},
    )

@app.get(API_PREFIX, response_model=BaseResponse)
@app.get(f"{API_PREFIX}/", response_model=BaseResponse, include_in_schema=False)
def root():
    return {
        "status": "success",
        "data": {"message": "PlantPulse API em execucao."},
    }

@app.get(f"{API_PREFIX}/health", response_model=BaseResponse)
def healthcheck():
    return {
        "status": "success",
        "data": {
            "service": "PlantPulse API",
            "status": "running",
        },
    }