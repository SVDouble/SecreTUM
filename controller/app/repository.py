import asyncio

import redis.asyncio as redis

from app.models import VariableUpdate, Source
from app.settings import Settings
from app.utils import async_lock, get_logger

__all__ = ["Repository"]

logger = get_logger(__file__)


class Repository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis = redis.from_url(self.settings.redis_url, decode_responses=True)

    async def get(self, key: str) -> float | int | str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: float | int | str):
        await self.redis.set(key, value)

    async def get_state(self) -> str:
        return await self.get("controller:state")

    async def set_state(self, state: str):
        await self.set("controller:state", state)

    async def get_gpio(self, pin: int) -> int | bool | None:
        return await self.get(f"gpio:{pin}")

    async def set_gpio(self, pin: int, value: int, source: Source):
        await self.set(f"gpio:{pin}", value)
        update = VariableUpdate(name=str(pin), value=value, source=source)
        await self.redis.publish("gpio", update.model_dump_json())

    async def drain(self):
        logger.info("Draining the chamber.")
        await self.start_pump(self.settings.drain_pump_pin)
        await asyncio.sleep(self.settings.drain_duration)
        await self.stop_pump(self.settings.drain_pump_pin)
        logger.info("Chamber drained.")

    async def fill_water(self):
        logger.info("Filling the chamber with water.")
        await self.start_pump(self.settings.water_pump_pin)
        await asyncio.sleep(self.settings.fill_duration)
        await self.stop_pump(self.settings.water_pump_pin)
        logger.info("Chamber filled with water.")

    async def fill_buffer(self):
        logger.info("Filling the chamber with buffer.")
        await self.start_pump(self.settings.buffer_pump_pin)
        await asyncio.sleep(self.settings.fill_duration)
        await self.stop_pump(self.settings.buffer_pump_pin)
        logger.info("Chamber filled with buffer.")

    @async_lock
    async def start_pump(self, pump_pin: int):
        await self.set_gpio(pump_pin, 1, source=Source.CONTROLLER)
        await self.set(f"pump_{pump_pin}", 1)

    @async_lock
    async def stop_pump(self, pump_pin: int):
        await self.set_gpio(pump_pin, 0, source=Source.CONTROLLER)
        await self.set(f"pump_{pump_pin}", 0)

    async def read_measurement(self):
        # TODO
        await asyncio.sleep(5)
        return 42

    async def check_optical_sensor(self) -> bool:
        return bool(await self.get_gpio(self.settings.optical_sensor_pin))
