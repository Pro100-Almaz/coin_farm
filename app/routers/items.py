from fastapi import APIRouter, HTTPException
from app.models import User
from app.crud import create_item, get_item

router = APIRouter()

@router.post("/items/", response_model=User)
async def create_item_endpoint(item: User):
    db_item = await create_item(item)
    if db_item:
        return db_item
    raise HTTPException(status_code=400, detail="Failed to create item")

@router.get("/items/{item_id}", response_model=User)
async def read_item_endpoint(item_id: int):
    item = await get_item(item_id)
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")
