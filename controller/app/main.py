import asyncio

from app.controller import Controller
from app.fastapi_backend import app
from app.gpiod_backend import GPIODBackend
from app.repository import Repository
from app.settings import Settings


async def main():
    settings = Settings()
    repository = Repository(settings)
    controller = Controller(repository)
    gpio_backend = GPIODBackend(repository)

    # Initialize state
    await repository.set_state("state", Controller.State.INITIAL_WASH)
    await repository.set_state("pump_activated", "0")
    await repository.set_state("sensor_value", "42")  # Example initial sensor value

    # Start the statechart and GPIO backend
    controller_main_loop_task = asyncio.create_task(controller.main_loop())
    gpio_main_loop_task = asyncio.create_task(gpio_backend.monitor_gpio())

    # Start FastAPI
    import uvicorn

    config = uvicorn.Config(
        app, host="0.0.0.0", port=8000, log_level=settings.log_level.lower()
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted")
