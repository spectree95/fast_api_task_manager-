from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.core.database import get_db
from app.models.users import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    
    payload = decode_access_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")
    
    db_user = db.execute(
        select(User).where(User.id == int(user_id))
        ).scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")
    
    return db_user