from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from .models import User
from .schemas import UserCreate
from app.utils import SECRET_KEY, ALGORITHM

from app.database import database


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="get_token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = database.fetchrow(
        """
        SELECT *
        FROM public.user
        WHERE telegram_id = $1 
        """, telegram_id
    )
    if user is None:
        raise credentials_exception
    return user

@router.get("/get_user")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/create_user")
async def create_user(new_user: UserCreate):
    print(new_user.data)
    telegram_id = new_user.data.get("id")
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid telegram_id"
        )

    return {"Status": 200}

