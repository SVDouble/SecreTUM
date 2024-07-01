import asyncio

from app.repository import Repository

__all__ = ["Controller"]


class Controller:
    class State:
        INITIAL_WASH = 1
        IDLE = 2
        MEASURE = 3
        POST_MEASURE_WASH = 4

    def __init__(self, repository: Repository, wash_duration=5, pump_duration=1):
        self.wash_duration = wash_duration
        self.pump_duration = pump_duration
        self.repository = repository

    async def wash_tube(self):
        await self.repository.start_wash()
        await asyncio.sleep(self.wash_duration)
        await self.repository.stop_wash()
        await self.transition_state()

    async def activate_pump(self):
        pump_activated = await self.repository.get_state("pump_activated") == "1"
        if not pump_activated:
            await self.repository.start_pump()
            await self.repository.set_state("pump_activated", "1")
        else:
            await asyncio.sleep(self.pump_duration)
            await self.repository.stop_pump()
            await self.repository.set_state("pump_activated", "0")
            await self.transition_state()

    async def measure_x(self):
        await self.activate_pump()
        pump_activated = await self.repository.get_state("pump_activated") == "1"
        if not pump_activated:
            sensor_value = await self.repository.read_sensor()
            print(f"Measured X: {sensor_value}")
            await self.repository.set_state("state", self.State.POST_MEASURE_WASH)

    async def check_optical_sensor(self):
        if await self.repository.check_optical_sensor():
            await self.repository.set_state("state", self.State.MEASURE)

    async def transition_state(self):
        state = int(await self.repository.get_state("state"))
        if state == self.State.INITIAL_WASH:
            await self.repository.set_state("state", self.State.IDLE)
        elif state == self.State.MEASURE:
            await self.repository.set_state("state", self.State.POST_MEASURE_WASH)
        elif state == self.State.POST_MEASURE_WASH:
            await self.repository.set_state("state", self.State.IDLE)

    async def main_loop(self):
        while True:
            state = int(await self.repository.get_state("state"))
            if state in [self.State.INITIAL_WASH, self.State.POST_MEASURE_WASH]:
                await self.wash_tube()
            elif state == self.State.IDLE:
                await self.check_optical_sensor()
            elif state == self.State.MEASURE:
                await self.measure_x()
            await asyncio.sleep(0.1)  # Add a small delay to prevent CPU overuse
