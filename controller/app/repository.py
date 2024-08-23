import asyncio
import random

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

    async def get_gpio(self, pin: int) -> int | None:
        value = await self.get(f"gpio:{pin}")
        if value is not None:
            value = int(value)
        return value

    async def set_gpio(self, pin: int, value: int, source: Source = Source.CONTROLLER):
        await self.set(f"gpio:{pin}", value)
        update = VariableUpdate(name=str(pin), value=value, source=source)
        await self.redis.publish("gpio", update.model_dump_json())

    @async_lock
    async def start_pump(self, motor: tuple[int, int], backward: bool = False):
        await self.set_gpio(motor[0], int(backward))
        await self.set_gpio(motor[1], int(not backward))

    @async_lock
    async def stop_pump(self, motor: tuple[int, int]):
        await self.set_gpio(motor[0], 0)
        await self.set_gpio(motor[1], 0)

    async def drain(self):
        logger.info("Draining the chamber.")
        await self.start_pump(self.settings.drain_pump)
        await asyncio.sleep(self.settings.drain_duration)
        await self.stop_pump(self.settings.drain_pump)
        await asyncio.sleep(self.settings.cooldown)
        logger.info("Chamber drained.")

    async def fill_water(self):
        logger.info("Filling the chamber with water.")
        await self.start_pump(self.settings.water_pump)
        await asyncio.sleep(self.settings.fill_duration_water)
        await self.stop_pump(self.settings.water_pump)
        await asyncio.sleep(self.settings.cooldown)
        logger.info("Chamber filled with water.")

    async def fill_buffer(self):
        logger.info("Filling the chamber with buffer.")
        await self.start_pump(self.settings.buffer_pump)
        await asyncio.sleep(self.settings.fill_duration_buffer)
        await self.stop_pump(self.settings.buffer_pump)
        await asyncio.sleep(self.settings.cooldown)
        logger.info("Chamber filled with buffer.")

    async def read_measurement(self):
        await asyncio.sleep(5)
        value = random.randint(0, 42)
        await self.set("controller:measurement", value)
        return value

    async def check_optical_sensor(self) -> bool:
        return bool(await self.get_gpio(self.settings.optical_sensor_pin))
