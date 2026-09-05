from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.users import router as user_router
from app.routes.applications import router as applications_router
from app.routes.companies import router as company_route

app = FastAPI(
    title="welcome to the jobtracking portal",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=user_router)
app.include_router(router=applications_router)
app.include_router(router=company_route)

@app.get("/")
def get_home():
    return {
        "message": "Welcome to the Job Application Tracking Portal"
    }