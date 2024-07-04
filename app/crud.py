from app.database import database
from app.routers.user.models import User

async def create_item(item: User):
    query = """
    INSERT INTO items (name, telegram_id, sign_up_date, last_login_date) 
    VALUES ($1, $2, $3, $4) 
    RETURNING id, name, telegram_id, sign_up_date, last_login_date
    """
    return await database.fetchrow(query, item.name, item.telegram_id, item.sign_up_date, 0)

async def get_item(item_id: int):
    query = "SELECT id, name, description, price FROM items WHERE id = $1"
    return await database.fetchrow(query, item_id)
