from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.core.database import get_session
from app.models.models import User

from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import get_password_hash, create_access_token, verify_password

router = APIRouter()

@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    user.password_hash = get_password_hash(user.password_hash) 
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/", response_model=List[User])
def read_users(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
