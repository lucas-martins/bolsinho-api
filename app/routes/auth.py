from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from ..database import SessionLocal
from .. import models, schemas
import bcrypt

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)) 

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    new_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        password=hashed_password.decode('utf-8')
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "Usuário criado com sucesso"}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if not db_user:
        db_user = db.query(models.User).filter(models.User.email == user.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

