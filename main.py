from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from datetime import datetime

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    password: str
class Post(BaseModel):
    id: int
    title: str
    body: str
    user_id: int
    category: str
    subcategory: str
    created_at: datetime
    longitude: float
    latitude: float
    image_url: str
    is_active: bool
    

    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/users/", response_model=User)
def create_user(user: User, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/posts/", response_model=Post)
def create_post(post: Post, db: db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
"""
@app.get("/posts/", response_model=List[Post])
def read_posts(skip: int = 0, limit: int = 10, db: db_dependency):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 10, db: db_dependency):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

"""