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
    buffer_pump_pin: int = 20
    water_pump_pin: int = 21
    drain_pump_pin: int = 22
    optical_sensor_pin: int = 23

    # Redis URL
    redis_url: str

    # GPIO enable flag
    gpio_enabled: bool = True

    # Timing configurations (in seconds)
    wash_duration: int = 5  # Duration for the wash cycle
    pump_duration: int = 1  # Duration for pumping the analyte or buffer
    drain_duration: int = 3  # Duration for draining the chamber
    fill_duration: int = 2  # Duration for filling the chamber with water or buffer

    # Default state
    default_state: str = "idle"  # Default starting state of the system
