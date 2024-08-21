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
    buffer_pump_pin: int = 1
    water_pump_pin: int = 2
    drain_pump_pin: int = 3
    optical_sensor_pin: int = 4

    # Redis URL
    redis_url: str = "redis://localhost"

    # GPIO enable flag
    gpio_enabled: bool = False

    # Timing configurations (in seconds)
    wash_duration: int = 5  # Duration for the wash cycle
    pump_duration: int = 1  # Duration for pumping the analyte or buffer
    drain_duration: int = 3  # Duration for draining the chamber
    fill_duration: int = 2  # Duration for filling the chamber with water or buffer

    # Additional configurations
    measurement_interval: int = 10  # Interval for checking the optical sensor
    idle_timeout: int = 60  # Timeout before transitioning to idle state automatically

    # Sensor thresholds (if applicable)
    optical_sensor_threshold: float = 0.5  # Example threshold for the optical sensor
    x_sensor_threshold: float = 1.0  # Example threshold for the X sensor

    # Logging configurations
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Default state
    default_state: str = "idle"  # Default starting state of the system
