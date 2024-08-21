from typing import Literal

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

__all__ = ["Settings"]


class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    title: str = "SecreTUM"
    version: str = "v0.1.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"

    # GPIO Pins
    buffer_pump_pin: int = 2
    target_pump_pin: int = 3
    optical_sensor_pin: int = 4
    x_sensor_pin: int = 34

    # Redis URL
    redis_url: str = "redis://localhost"

    # GPIO enable flag
    gpio_enabled: bool = False
