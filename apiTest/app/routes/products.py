from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Product, ProductCreate
from app.db import products_db
import asyncio

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[Product])
async def list_products():
    """Returns a list of all products in the system."""
    await asyncio.sleep(0.1)
    return products_db

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate):
    """Creates a new product."""
    new_product = {
        "id": len(products_db) + 1,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }
    products_db.append(new_product)
    return new_product

@router.put("/{product_id}/stock", response_model=Product)
async def update_stock(product_id: int, quantity: int):
    """Updates the stock of a product."""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product["stock"] = quantity
    return product

@router.get("/search", response_model=List[Product])
async def search_products(query: str):
    """Searches products by name."""
    results = [p for p in products_db if query.lower() in p["name"].lower()]
    return results
