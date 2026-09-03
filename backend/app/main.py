from fastapi import FastAPI


from app.router.users import router as user_router
from app.router.tasks import router as task_router



app = FastAPI()

app.include_router(user_router)
app.include_router(task_router)


@app.get("/")
def root():
    return {
        "message" : "Task manager API"
    }