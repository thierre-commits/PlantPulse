import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.schemas import AnalysisResponse
from data_processing.basic_analysis import analyze_signals
from data_processing.read_data import fetch_recent_signals


router = APIRouter(tags=["analysis"])
logger = logging.getLogger("plantpulse.api")


@router.get("/analysis", response_model=AnalysisResponse)
def get_analysis(
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

        return {"status": "success", "data": analyze_signals(data)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.error("Erro interno no endpoint /analysis", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao gerar analise.",
        ) from error
