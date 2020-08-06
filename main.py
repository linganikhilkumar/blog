from typing import List

import uvicorn
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException

import models, schemas, crud
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()



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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)