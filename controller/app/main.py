import asyncio

from app.api import app
from app.controller import Controller
from app.gpio import GPIOBackend
from app.repository import Repository
from app.settings import Settings


async def main():
    settings = Settings()
    repository = Repository(settings)
    controller = Controller(repository)

    # Initialize state
    await repository.set_state(Controller.State.INITIAL_WASH)

    # Start the statechart and GPIO backend
    loops = [asyncio.create_task(controller.main_loop())]
    if settings.gpio_enabled:
        gpio_backend = GPIOBackend(repository)
        loops.append(asyncio.create_task(gpio_backend.monitor()))

    # Start FastAPI
    import uvicorn

    config = uvicorn.Config(
        app, host="0.0.0.0", port=8000, log_level=settings.log_level.lower()
    )
    server = uvicorn.Server(config)
    await server.serve()

    for loop in loops:
        loop.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted")
