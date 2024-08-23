import asyncio

import uvicorn

from app.api import app
from app.controller import Controller
from app.gpio import GPIOBackend
from app.repository import Repository
from app.settings import Settings


async def main():
    settings = Settings()
    repository = Repository(settings)
    controller = Controller(repository)

    # FastAPI
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower(),
        reload=True,
    )
    server = uvicorn.Server(config)

    # Run all the tasks
    loops = [controller.main_loop(), server.serve()]
    if settings.gpio_enabled:
        gpio_backend = GPIOBackend(
            repository,
            input_pins=[settings.optical_sensor_pin],
            output_pins=[
                settings.buffer_pump_pin,
                settings.water_pump_pin,
                settings.drain_pump_pin,
            ],
        )
        loops.append(asyncio.create_task(gpio_backend.monitor()))
    await asyncio.gather(*loops)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted")
