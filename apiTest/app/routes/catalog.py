from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from app.db import products_db

router = APIRouter(prefix="/catalog", tags=["catalog"])

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

@router.get("/products")
def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Lists products with optional filters."""
    results = products_db

    if category:
        results = [p for p in results if p.get("category") == category]
    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    if in_stock:
        results = [p for p in results if p["stock"] > 0]

    return results[skip : skip + limit]

@router.get("/products/{product_id}")
def get_product(product_id: int):
    """Returns details for a specific product."""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", status_code=201)
def create_product(product: ProductCreate):
    """Creates a new product in the catalog."""
    new_id = max((p["id"] for p in products_db), default=0) + 1
    new_product = {"id": new_id, **product.model_dump()}
    products_db.append(new_product)
    return new_product

@router.patch("/products/{product_id}")
def update_product(product_id: int, updates: ProductUpdate):
    """Partially updates a product."""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        product[field] = value

    return product

@router.get("/categories")
def list_categories():
    """Returns all unique product categories."""
    categories = list({p.get("category") for p in products_db if p.get("category")})
    return sorted(categories)
