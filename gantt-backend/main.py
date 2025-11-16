import sys
import os

sys.path.append(os.path.dirname(__file__))
import fastapi
from app.api.auth import router as auth_router
from app.api.team import router as team_router
from app.api.project import router as project_router
from app.api.stream import router as stream_router
from app.api.goal import router as goal_router
from app.api.user import router as user_router
from app.api.task import router as task_router
from app.api.meta import router as meta_router

app = fastapi.FastAPI(title="Task Tracker API")
app.include_router(auth_router)
app.include_router(team_router)

app.include_router(project_router)
app.include_router(stream_router)
app.include_router(goal_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(meta_router)


@app.get("/")
def read_root():
    return {"message": "Task Tracker API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
