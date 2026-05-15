from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    id: int
    username: str
    email: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]

class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    total_price: float
    status: str
