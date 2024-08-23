from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.repository import Repository
from app.settings import Settings
from app.utils import get_logger

app = FastAPI(root_path="/app")
# TODO: pass /app as environment variable
settings = Settings()
repository = Repository(settings)
logger = get_logger(__file__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StateModel(BaseModel):
    state: str


@app.post("/state")
async def update_state(state_model: StateModel):
    current_state = await repository.get_state()
    logger.info(
        f"Current state: {current_state}. "
        f"Requested state change to: {state_model.state}."
    )

    if current_state != "idle":
        logger.warning(
            f"State change denied. Current state '{current_state}' is not 'idle'."
        )
        raise HTTPException(
            status_code=400,
            detail="State can only be changed if the current state is 'idle'",
        )

    await repository.set_state(state_model.state)
    logger.info(
        f"State changed successfully from '{current_state}' to '{state_model.state}'."
    )
    return {"status": f"state_set_to_{state_model.state}"}


@app.get("/state")
async def get_state():
    current_state = await repository.get_state()
    logger.info(f"Retrieved current state: {current_state}.")
    return {"state": current_state}
