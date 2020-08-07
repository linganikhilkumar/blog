from typing import List

#import uvicorn
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException
import models, schemas, crud
from database import engine, SessionLocal
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from mangum import Mangum

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

def get_db(request: Request):
    return request.state.db

@app.get("/")
def root():
    message={
        "message": "hello"
    }
    return message

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    data=crud.get_all_usernames(db)
    #for i in data
    return data
@app.get("/user/{username}", response_model=schemas.UserInfo)
def get_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(status_code=404, detail="Username not registered")
    return crud.get_user_by_username(db, username=username)

@app.post("/user", response_model=schemas.UserInfo)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

handler = Mangum(app, spec_version=2)
