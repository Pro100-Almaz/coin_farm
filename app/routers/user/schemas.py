from pydantic import BaseModel

class User(BaseModel):
    data: dict

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "dict": {
                        "id": str,
                        "username": str,
                        "first_name": str,
                        "last_name": str,
                        "language_code": str,
                        "allows_write_to_pm": bool
                    }
                }
            ]
        }
    }

class UserLogin(BaseModel):
    telegram_id: int
    username: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "telegram_id": int,
                    "username": str
                }
            ]
        }
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


class UserLevel(BaseModel):
    user_points: int
    max_points: int
    current_lvl: int


