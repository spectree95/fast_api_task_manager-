from pwdlib import PasswordHash
import jwt
from jwt import InvalidTokenError
from fastapi import HTTPException,status
from datetime import datetime, timedelta, timezone

from app.core.config import settings


password_hash = PasswordHash.recommended()

def hash_password(password : str) -> str:
    return password_hash.hash(password)
    

def verify_password(password:str, hashed_password: str) -> bool:
    return password_hash.verify(password,hashed_password)

def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({'exp':expire})
    
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def decode_access_token(token:str) -> dict:
    try:
        payload = jwt.decode(
            jwt = token,
            key = settings.SECRET_KEY,
            algorithms = [settings.ALGORITHM],
        )
        return payload
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    