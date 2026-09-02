from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.model import User
from app.schemas import UserResponse, UserCreate,UserLogin
from app.auth import create_access_token
from app.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["User"]
)
password_hasher  = PasswordHash.recommended()
@router.post("/",response_model=UserResponse)
def create_user(
    user:UserCreate,
    db: Session = Depends(get_db)
):
    
    hashed_pass = password_hasher.hash(user.password)
    db_user = User(
        name=user.name,
        email = user.email,
        password_hash = hashed_pass
    )

    db.add(db_user)
    try:

        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    return db_user


@router.post("/login")
def user_login(
    user : UserLogin,
    db:Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email==user.email).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Mail or Password"
        )

    if not password_hasher.verify(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(db_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user
