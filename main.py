import uuid
from fastapi import APIRouter, FastAPI, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext
import bcrypt
import auth
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import Response
username = "testuser"
password = "testpassword"


def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode('utf8')
    return string_password


def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)


app = FastAPI()
router = APIRouter()
security = HTTPBasic()
#app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine)

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    password: str
    class Config:
        orm_mode = True

class UserCreate(CreateUser):
    pass
class CreatePost(BaseModel):
    title: str
    body: str
    user_id: int
    category: str
    subcategory: str = None
    longitude: float = None
    latitude: float = None
    image_url: str = None
    is_active: bool = True

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
    class Config:
        orm_mode = True
class PostCreate(CreatePost):
    pass
    

    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/users/", response_model=User)
def create_user(user: CreateUser, db: db_dependency):
    #db_user = models.User(**user.dict())
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/posts/", response_model=Post)
def create_post(post: CreatePost, db: db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/login/")
def login(username: str, password: str, db: db_dependency ):
    #user = db.query(models.User).filter(models.User.username == username, models.User.password == password).first()
    user = db.query(models.User).filter(models.User.username == username).first()
    if user and verify_password(password, user.password):
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": "Login successful", "user_id": user.id}

@app.get("/posts/by_user/{user_id}", response_model=List[Post])
def get_posts_by_user(user_id: int, db: db_dependency, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    posts = db.query(models.Post).filter(models.Post.user_id == user_id).all()
    return posts

@app.get("/posts/active/", response_model=List[Post])
def get_active_posts(db: db_dependency, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    posts = db.query(models.Post).filter(models.Post.is_active == True).all()
    return posts

@app.get("/posts/category/{category_name}", response_model=List[Post])
def get_posts_by_category(category_name: str, db: db_dependency, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    posts = db.query(models.Post).filter(models.Post.category == category_name).all()
    return posts

@app.get("/posts/all/", response_model=List[Post])
def get_all_posts(db: db_dependency, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    posts = db.query(models.Post).all()
    return posts

@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int, db: db_dependency, credentials: Annotated[HTTPBasicCredentials, Depends(security)]) :
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: int, updated_post: CreatePost, db: db_dependency, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in updated_post.dict().items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post 

@app.post("/upload-image/{post_id}")
async def upload_image(post_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        image_bytes = await file.read()

        new_image = models.Image(
            post_id=post_id,
            image_data=image_bytes,
            image_url=None  # optional
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)

        return {"message": "Image uploaded", "image_id": new_image.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""@app.get("/image/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=image.image_data,
        media_type="image/jpeg"   # or detect automatically
    )"""

@app.get("/image/{post_id}")
def get_post_image(post_id: int, db: Session = Depends(get_db)):
    image = (
        db.query(models.Image)
        .filter(models.Image.post_id == post_id)
        .first()
    )

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=image.image_data,
        media_type="image/jpeg"
    )

