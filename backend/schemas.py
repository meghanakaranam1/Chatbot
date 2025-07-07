from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    name: str
    email: str
    age: int
    city: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock_quantity: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order schemas
class OrderBase(BaseModel):
    user_id: int
    status: str

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    total_amount: float
    order_date: datetime
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    data: Optional[List[dict]] = None
    query_type: Optional[str] = None

class QueryRequest(BaseModel):
    natural_language_query: str
    
class QueryResponse(BaseModel):
    sql_query: str
    results: List[dict]
    explanation: str 