from typing import Any

from pydantic import BaseModel


class BaseResponse(BaseModel):
    status: str
    message: str | None = None
    data: Any = None


class SignalsResponse(BaseResponse):
    data: list[Any]


class AnalysisResponse(BaseResponse):
    data: dict[str, Any] | list[Any]
