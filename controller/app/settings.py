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
    buffer_pump: tuple[int, int] = (5, 6)
    water_pump: tuple[int, int] = (22, 23)
    drain_pump: tuple[int, int] = (27, 17)
    optical_sensor_pin: int = 4

    # Redis URL
    redis_url: str

    # GPIO enable flag
    gpio_enabled: bool = True

    # Timing configurations (in seconds)
    drain_duration: float = 2  # Duration for draining the chamber
    fill_duration_buffer: float = 0.25
    fill_duration_water: float = 0.1
    cooldown: float = 1

    # Meta
    recycle_cycles: int = 5

    # Default state
    default_state: str = "idle"  # Default starting state of the system
