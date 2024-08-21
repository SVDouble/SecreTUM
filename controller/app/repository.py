import redis.asyncio as redis

from app.models import VariableUpdate, Source
from app.settings import Settings
from app.utils import async_lock


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

    async def set_gpio(self, pin: int, value: int | bool, source: Source):
        value = int(value)
        await self.set(f"gpio:{pin}", value)
        update = VariableUpdate(name=str(pin), value=value, source=source)
        await self.redis.publish("gpio", update.model_dump_json())

    @async_lock
    async def start_wash(self):
        await self.set_gpio(
            self.settings.buffer_pump_pin, True, source=Source.CONTROLLER
        )
        await self.set("washing", 1)

    @async_lock
    async def stop_wash(self):
        await self.set_gpio(
            self.settings.buffer_pump_pin, False, source=Source.CONTROLLER
        )
        await self.set("washing", 0)

    @async_lock
    async def start_pump(self):
        await self.set_gpio(
            self.settings.target_pump_pin, True, source=Source.CONTROLLER
        )
        await self.set("pump", 1)

    @async_lock
    async def stop_pump(self):
        await self.set_gpio(
            self.settings.target_pump_pin, False, source=Source.CONTROLLER
        )
        await self.set("pump", 0)

    async def read_measurement(self):
        return await self.get_gpio(self.settings.x_sensor_pin)

    async def check_optical_sensor(self) -> bool:
        return bool(await self.get_gpio(self.settings.optical_sensor_pin))
