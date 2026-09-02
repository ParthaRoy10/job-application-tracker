from sqlalchemy import text 
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import FastAPI,Depends

app = FastAPI(
    title = "Job application tracker"
)


@app.get("/")
def get_home():
    return {
        "message":"welcome to the jobtracking portal"
    }


@app.get("/db_test")
def get_db_test(db : Session = Depends(get_db)):
    result = db.execute(text("Select 1;"))
    return {
        "Status" : "Connected",
        "Result" : result.scalar()
    }
