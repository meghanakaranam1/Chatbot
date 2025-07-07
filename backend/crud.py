from sqlalchemy.orm import Session
from sqlalchemy import text
from database.models import User, Product, Order, OrderItem
from backend.schemas import UserCreate, ProductCreate, OrderCreate
from typing import List, Dict, Any

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()

def get_products_by_category(db: Session, category: str):
    return db.query(Product).filter(Product.category == category).all()

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).offset(skip).limit(limit).all()

def get_orders_by_user(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()

def get_orders_by_status(db: Session, status: str):
    return db.query(Order).filter(Order.status == status).all()

def create_order(db: Session, order: OrderCreate):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def execute_sql_query(db: Session, sql_query: str) -> List[Dict[str, Any]]:
    """Execute a raw SQL query and return results as list of dictionaries"""
    try:
        result = db.execute(text(sql_query))
        columns = result.keys()
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return [{"error": str(e)}]

def get_database_schema(db: Session) -> Dict[str, Any]:
    """Get database schema information for LLM context"""
    schema_info = {
        "tables": {
            "users": {
                "columns": ["id", "name", "email", "age", "city", "created_at"],
                "description": "User information including demographics"
            },
            "products": {
                "columns": ["id", "name", "description", "price", "category", "stock_quantity", "created_at"],
                "description": "Product catalog with pricing and inventory"
            },
            "orders": {
                "columns": ["id", "user_id", "total_amount", "status", "order_date"],
                "description": "Customer orders with status and totals"
            },
            "order_items": {
                "columns": ["id", "order_id", "product_id", "quantity", "price"],
                "description": "Individual items within orders"
            }
        },
        "relationships": [
            "users.id -> orders.user_id (one-to-many)",
            "orders.id -> order_items.order_id (one-to-many)", 
            "products.id -> order_items.product_id (one-to-many)"
        ]
    }
    return schema_info 