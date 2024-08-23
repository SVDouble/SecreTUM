from enum import StrEnum

from pydantic import BaseModel

__all__ = ["Source", "VariableUpdate"]


class Source(StrEnum):
    CONTROLLER = "controller"
    GPIO = "gpio"
    API = "api"


class VariableUpdate(BaseModel):
    name: str
    value: int
    source: Source
