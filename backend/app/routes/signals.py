import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.schemas import SignalsResponse
from data_processing.read_data import fetch_recent_signals


router = APIRouter(tags=["signals"])
logger = logging.getLogger("plantpulse.api")


@router.get("/signals", response_model=SignalsResponse)
def get_signals(
    limit: Annotated[int, Query(gt=0, le=1000)],
    sensor_id: Annotated[str | None, Query(min_length=1)] = None,
):
    try:
        data = fetch_recent_signals(limit=limit, sensor_id=sensor_id)

        if not data:
            return {
                "status": "success",
                "data": [],
                "message": "Nenhum dado encontrado",
            }

        return {"status": "success", "data": data}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.error("Erro interno no endpoint /signals", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao buscar sinais.",
        ) from error
