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
    def __init__(
        self, repository: Repository, input_pins: list[int], output_pins: list[int]
    ):
        self.repository = repository
        self.settings = repository.settings

        self.input_devices = {pin: DigitalInputDevice(pin) for pin in input_pins}
        self.output_devices = {pin: DigitalOutputDevice(pin) for pin in output_pins}

    async def set_gpio(self, pin: int, value: int):
        if pin not in self.output_devices:
            raise ValueError(f"Pin {pin} not permitted for GPIO access")
        target = self.output_devices[pin]
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
            for pin, device in self.input_devices.items():
                value = 1 if device.is_active else 0
                previous_value = await self.repository.get_gpio(pin)
                if value != previous_value:
                    await self.repository.set_gpio(pin, value, source=Source.GPIO)
            await asyncio.sleep(0.01)

    async def monitor(self):
        await asyncio.gather(self.monitor_redis(), self.monitor_gpio())
