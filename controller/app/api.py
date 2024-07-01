from fastapi import FastAPI
from app.repository import Repository
from app.settings import Settings

app = FastAPI()
settings = Settings()
repository = Repository(settings)


@app.post("/start_wash")
async def start_wash():
    await repository.start_wash()
    return {"status": "wash_started"}


@app.post("/stop_wash")
async def stop_wash():
    await repository.stop_wash()
    return {"status": "wash_stopped"}


@app.post("/start_pump")
async def start_pump():
    await repository.start_pump()
    return {"status": "pump_started"}


@app.post("/stop_pump")
async def stop_pump():
    await repository.stop_pump()
    return {"status": "pump_stopped"}


@app.get("/read_sensor")
async def read_sensor():
    sensor_value = await repository.read_measurement()
    return {"value": sensor_value}


@app.get("/check_optical_sensor")
async def check_optical_sensor():
    optical_sensor = await repository.check_optical_sensor()
    return {"value": optical_sensor}
