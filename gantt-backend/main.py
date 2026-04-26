import os
import sys

sys.path.append(os.path.dirname(__file__))
import fastapi

from app.api.auth import router as auth_router
from app.api.goal import router as goal_router
from app.api.meta import router as meta_router
from app.api.project import router as project_router
from app.api.stream import router as stream_router
from app.api.task import router as task_router
from app.api.team import router as team_router
from app.api.user import router as user_router
from app.api.reminder import router as reminder_router
from app.api.push import router as push_router
from app.core import middleware
from app.core.db import engine
from app.models.base import Base
from app.core.scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = fastapi.FastAPI(title="Task Tracker API")
app.middleware("http")(middleware.auth_middleware)

app.include_router(auth_router)
app.include_router(team_router)

app.include_router(project_router)
app.include_router(stream_router)
app.include_router(goal_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(meta_router)

app.include_router(reminder_router)
app.include_router(push_router)

@app.get("/")
def read_root():
    return {"message": "Task Tracker API"}

@app.on_event("startup")
async def startup_event():
    start_scheduler()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
