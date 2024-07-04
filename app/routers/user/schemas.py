from pydantic import BaseModel

class UserCreate(BaseModel):
    data: dict
    # id: str
    # username: str
    # first_name: str
    # last_name: str
    # language_code: str
    # allows_write_to_pm: bool

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TelegramLogin(BaseModel):
    telegram_id: str
