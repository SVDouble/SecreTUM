from asyncio import Lock

import redis.asyncio as redis

from app.settings import Settings
from app.utils import async_lock


class Repository:
    def __init__(self, settings: Settings):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        self.settings = settings
        self.gpio_enabled = settings.enable_gpio
        self.lock = Lock()
        self.gpio_off = None
        self.gpio_on = None
        if self.gpio_enabled:
            import gpiod

            self.gpio_off = gpiod.line.Value(0)
            self.gpio_on = gpiod.line.Value(1)
            direction = gpiod.line.Direction
            self.chip = gpiod.Chip("/dev/gpiochip0")
            self.buffer_pump_request = self.chip.request_lines(
                config={
                    (self.settings.buffer_pump_pin,): gpiod.LineSettings(
                        direction=direction.OUTPUT
                    )
                },
                consumer="buffer_pump",
            )
            self.target_pump_request = self.chip.request_lines(
                config={
                    (self.settings.target_pump_pin,): gpiod.LineSettings(
                        direction=direction.OUTPUT
                    )
                },
                consumer="target_pump",
            )
            self.optical_sensor_request = self.chip.request_lines(
                config={
                    (self.settings.optical_sensor_pin,): gpiod.LineSettings(
                        direction=direction.INPUT
                    )
                },
                consumer="optical_sensor",
            )

    @async_lock
    async def set_state(self, key, value):
        await self.redis.set(key, value)

    @async_lock
    async def get_state(self, key):
        return await self.redis.get(key)

    @async_lock
    async def start_wash(self):
        if self.gpio_enabled:
            self.buffer_pump_request.set_values(
                {self.settings.buffer_pump_pin: self.gpio_on}
            )
        await self.set_state("washing", True)

    @async_lock
    async def stop_wash(self):
        if self.gpio_enabled:
            self.buffer_pump_request.set_values(
                {self.settings.buffer_pump_pin: self.gpio_off}
            )
        await self.set_state("washing", False)

    @async_lock
    async def start_pump(self):
        if self.gpio_enabled:
            self.target_pump_request.set_values(
                {self.settings.target_pump_pin: self.gpio_on}
            )
        await self.set_state("pump", True)

    @async_lock
    async def stop_pump(self):
        if self.gpio_enabled:
            self.target_pump_request.set_values(
                {self.settings.target_pump_pin: self.gpio_off}
            )
        await self.set_state("pump", False)

    @async_lock
    async def read_sensor(self):
        # Placeholder for actual sensor read logic
        return await self.get_state("sensor_value")

    @async_lock
    async def check_optical_sensor(self):
        if self.gpio_enabled:
            events = self.optical_sensor_request.read_edge_events()
            return events is not None
        return False  # Default value when GPIO is disabled
