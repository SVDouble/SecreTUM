import asyncio
from enum import StrEnum

import numpy as np
from scipy.optimize import curve_fit

from app.repository import Repository
from app.utils import get_logger

__all__ = ["Controller"]

logger = get_logger(__file__)


class Controller:
    class State(StrEnum):
        IDLE = "idle"
        MEASURE = "measure"
        RECYCLING = "recycle"

    def __init__(self, repository: Repository):
        self.repository = repository
        self.settings = repository.settings

    async def start_recycling(self):
        logger.info("Starting recycling process.")

        await self.repository.drain()
        for i in range(self.settings.recycle_cycles):
            logger.info(
                f"Recycling: cycle {i + 1} out of {self.settings.recycle_cycles}."
            )
            await self.repository.fill_water()
            await self.repository.drain()
        await self.repository.fill_buffer()

        logger.info("Recycling process completed.")
        await self.transition_state(self.State.IDLE)

    async def get_concentration(self, measured_capacitance: float) -> float:
        reference_concentration = np.array(self.settings.reference_concentration)  # 10^n nanograms/mL
        reference_capacitance = np.array(self.settings.reference_capacitance)  # Capacitance values

        # Define the linear model for fitting: C = a * log(concentration) + b
        def linear_model(x, a, b):
            return a * np.log10(x) + b

        # Perform linear regression to find the best fit line in the log domain
        reference_coefficients = curve_fit(linear_model, reference_concentration, reference_capacitance)[0]

        # Function to calculate concentration given a new capacitance
        def calculate_concentration(new_capacitance, coefficients):
            a, b = coefficients
            concentration_estimated = 10 ** ((new_capacitance - b) / a)
            return concentration_estimated

        return calculate_concentration(measured_capacitance, reference_coefficients)

    async def conduct_measurement(self):
        logger.info("Starting capacitance measurement.")
        sensor_value = await self.repository.read_measurement()
        logger.debug(f"Measured capacitance: {sensor_value}")
        await self.repository.set("controller:capacitance", sensor_value)
        concentration = await self.get_concentration(sensor_value)
        await self.repository.set("controller:concentration", concentration)
        await self.transition_state(self.State.RECYCLING)

    async def check_optical_sensor(self):
        if await self.repository.check_optical_sensor():
            logger.info("Optical sensor triggered, transitioning to measurement state.")
            await self.transition_state(self.State.MEASURE)

    async def transition_state(self, next_state: State):
        current_state = await self.repository.get_state()
        logger.info(f"Transitioning from '{current_state}' to '{next_state}'.")
        await self.repository.set_state(next_state)

    async def main_loop(self):
        initial_state = Controller.State(self.settings.default_state)
        await self.repository.set_state(initial_state)
        logger.debug(f"Setting state to the initial state '{initial_state}'.")
        while True:
            state = await self.repository.get_state()
            if state == self.State.IDLE:
                await self.repository.set_led(1)
                await self.check_optical_sensor()
            elif state == self.State.MEASURE:
                await asyncio.sleep(self.settings.measurement_delay)
                await self.repository.set_led(0)
                await self.conduct_measurement()
            elif state == self.State.RECYCLING:
                await self.repository.set_led(1)
                await self.start_recycling()
            await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse
