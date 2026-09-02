from fastapi import FastAPI

from app.routes.users import router as user_router
from app.routes.applications import router as applications_router


app = FastAPI(
    title="welcome to the jobtracking portal",
)


app.include_router(router=user_router)
app.include_router(router=applications_router)

@app.get("/")
def get_home():
    return {
        "message": "Welcome to the Job Application Tracking Portal"
    }