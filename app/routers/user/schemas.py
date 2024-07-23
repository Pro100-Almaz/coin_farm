from pydantic import BaseModel

class User(BaseModel):
    data: dict

class UserLogin(BaseModel):
    telegram_id: int
    username: str


class Token(BaseModel):
    access_token: str
    user_id: int
    telegram_id: int
    username: str


class TelegramLogin(BaseModel):
    telegram_id: str

class Subscriptions(BaseModel):
    user_id: int

class Subscribers(BaseModel):
    user_id: int
    gain_points: int


class UserPoints(BaseModel):
    gain_points: int | float

class UserLevel(BaseModel):
    new_user_lvl: int
