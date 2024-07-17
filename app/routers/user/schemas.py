from pydantic import BaseModel

class User(BaseModel):
    data: dict

    class Config:
        schema_extra = {
            "examples": [
                {
                    "data": {
                        "id": "user_id",
                        "username": "user_name",
                        "first_name": "First",
                        "last_name": "Last",
                        "language_code": "en",
                        "allows_write_to_pm": True
                    }
                }
            ]
        }

class UserLogin(BaseModel):
    telegram_id: int
    username: str

    class Config:
        schema_extra = {
            "examples": [
                {
                    "telegram_id": int,
                    "username": str
                }
            ]
        }


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
    user_id: int
    gain_points: int


class UserLevel(BaseModel):
    user_points: int
    max_points: int
    current_lvl: int
