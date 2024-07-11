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
    telegram_id: int
    username: str


class Token(BaseModel):
    access_token: str
    user_id: int
    telegram_id: int
    username: str


class User(BaseModel):
    id: int

class TelegramLogin(BaseModel):
    telegram_id: str

class Subscriptions(BaseModel):
    user_id: int

class Subscribers(BaseModel):
    user_id: int
    gain_points: int


class UserPoints(BaseModel):
    user_id: int

class UserLevel(BaseModel):
    user_id: int

