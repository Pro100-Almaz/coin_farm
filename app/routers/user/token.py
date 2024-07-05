from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
import jwt

from .schemas import Token, TelegramLogin
from app.utils import create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from app.database import database


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="get_token")


def authenticate_user(telegram_id: str, password: str):
    user = database.fetchrow(
        """
        SELECT *
        FROM public.user
        WHERE telegram_id = $1 
        """, telegram_id
    )
    if not user:
        return None

    return user

def generate_token(telegram_id: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": telegram_id}, expires_delta=access_token_expires
    )

    return access_token

@router.post("/get_token", response_model=Token)
async def login_for_access_token(telegram_login: TelegramLogin):
    telegram_id = telegram_login.telegram_id
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid telegram_id"
        )

    access_token = generate_token(telegram_id)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh_token", response_model=Token)
async def refresh_access_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        telegram_id: str = payload.get("sub")
        if telegram_id is None:
            raise credentials_exception
    except:
        raise credentials_exception

    access_token = generate_token(telegram_id)

    return {"access_token": access_token, "token_type": "bearer"}