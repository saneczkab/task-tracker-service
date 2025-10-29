import sys
import os

sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from api.auth import router as auth_router

app = FastAPI(title="Task Tracker API")
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Task Tracker API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)