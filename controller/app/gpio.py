import asyncio

import gpiozero.pins.lgpio
import lgpio


def __patched_init(self, chip=None):
    gpiozero.pins.lgpio.LGPIOFactory.__bases__[0].__init__(self)
    chip = 0
    self._handle = lgpio.gpiochip_open(chip)
    self._chip = chip
    self.pin_class = gpiozero.pins.lgpio.LGPIOPin


gpiozero.pins.lgpio.LGPIOFactory.__init__ = __patched_init

from gpiozero import DigitalOutputDevice, DigitalInputDevice

from app.models import Source, VariableUpdate
from app.repository import Repository
from app.utils import get_logger

__all__ = ["GPIOBackend"]

logger = get_logger(__file__)


class GPIOBackend:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.settings = repository.settings

        self.buffer_pump = DigitalOutputDevice(
            self.settings.buffer_pump_pin, initial_value=False
        )
        self.target_pump = DigitalOutputDevice(
            self.settings.target_pump_pin, initial_value=False
        )
        self.optical_sensor = DigitalInputDevice(self.settings.optical_sensor_pin)

    async def set_gpio(self, pin: int, value: int):
        if pin == self.settings.buffer_pump_pin:
            target = self.buffer_pump
        elif pin == self.settings.target_pump_pin:
            target = self.target_pump
        else:
            raise ValueError(f"Pin {pin} not permitted for GPIO access")
        if target.value != value:
            target.value = value

    async def monitor_redis(self):
        pubsub = self.repository.redis.pubsub()
        await pubsub.subscribe("gpio")
        async for message in pubsub.listen():
            if message["type"] == "message":
                update: VariableUpdate = VariableUpdate.model_load_json(message["data"])
                if update.source == Source.GPIO:
                    # Skip updates from GPIO to avoid infinite loop
                    continue
                try:
                    await self.set_gpio(int(update.name), update.value)
                except ValueError as e:
                    logger.error(f"Invalid GPIO pin: {update.name}", exc_info=e)

    async def monitor_gpio(self):
        while True:
            current_state = self.optical_sensor.is_active
            previous_state = await self.repository.get_gpio(
                self.settings.optical_sensor_pin
            )
            if current_state != previous_state:
                await self.repository.set_gpio(
                    self.settings.optical_sensor_pin, current_state, source=Source.GPIO
                )
            await asyncio.sleep(0.1)

    async def monitor(self):
        await asyncio.gather(self.monitor_redis(), self.monitor_gpio())
