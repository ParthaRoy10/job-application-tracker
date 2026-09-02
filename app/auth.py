from datetime import datetime, timedelta, timezone

import jwt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import JWTSettings
from app.database import get_db
from app.model import User

settings = JWTSettings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def create_access_token(user_id:int):
    expire = datetime.now(timezone.utc)+timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub" : str(user_id),
        "exp" : expire
    }

    encoded_jwt =  jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db:Session=Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authentication creds"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authentication creds"
        )

    db_user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authentication creds"
        )

    return db_user
