from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}}
)

# Sample in-memory storage
fake_items_db = {"item1": {"name": "Foo"}, "item2": {"name": "Bar"}}

@router.get("/")
async def read_items():
    return fake_items_db

@router.get("/{item_id}")
async def read_item(item_id: str):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": fake_items_db[item_id]}

@router.post("/")
async def create_item(item_id: str, name: str):
    if item_id in fake_items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_items_db[item_id] = {"name": name}
    return {"item_id": item_id, "name": name}