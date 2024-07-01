import asyncio

from app.repository import Repository


class GPIODBackend:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def monitor_gpio(self):
        while True:
            # Example: Read GPIO values and update the repository
            sensor_value = await self.repository.read_sensor()
            await self.repository.set_state("sensor_value", sensor_value)
            # Add more logic to monitor GPIO and update the state as needed
            await asyncio.sleep(1)  # Adjust the interval as needed
