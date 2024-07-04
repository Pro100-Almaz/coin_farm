from datetime import datetime

from pydantic import BaseModel

class User(BaseModel):
    id: int = None
    name: str
    telegram_id: str = None
    sign_up_date: datetime = None
    last_login_date: datetime = None