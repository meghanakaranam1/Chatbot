from sqlalchemy.orm import Session
from database.database import SessionLocal, init_database
from database.models import User, Product, Order, OrderItem
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        # Create sample users
        users = [
            User(name="John Doe", email="john@example.com", age=30, city="New York"),
            User(name="Jane Smith", email="jane@example.com", age=25, city="Los Angeles"),
            User(name="Bob Johnson", email="bob@example.com", age=35, city="Chicago"),
            User(name="Alice Brown", email="alice@example.com", age=28, city="Houston"),
            User(name="Charlie Wilson", email="charlie@example.com", age=40, city="Phoenix"),
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        # Create sample products
        products = [
            Product(name="Laptop", description="High-performance laptop", price=999.99, category="Electronics", stock_quantity=50),
            Product(name="Smartphone", description="Latest model smartphone", price=699.99, category="Electronics", stock_quantity=100),
            Product(name="Headphones", description="Wireless noise-canceling headphones", price=199.99, category="Electronics", stock_quantity=75),
            Product(name="Book", description="Programming fundamentals book", price=39.99, category="Books", stock_quantity=200),
            Product(name="Coffee Mug", description="Ceramic coffee mug", price=12.99, category="Kitchen", stock_quantity=150),
            Product(name="Desk Chair", description="Ergonomic office chair", price=299.99, category="Furniture", stock_quantity=30),
            Product(name="Monitor", description="4K display monitor", price=349.99, category="Electronics", stock_quantity=40),
            Product(name="Keyboard", description="Mechanical gaming keyboard", price=89.99, category="Electronics", stock_quantity=80),
        ]
        
        for product in products:
            db.add(product)
        db.commit()
        
        # Create sample orders
        orders_data = [
            {"user_id": 1, "status": "completed", "order_date": datetime.now() - timedelta(days=10)},
            {"user_id": 2, "status": "completed", "order_date": datetime.now() - timedelta(days=8)},
            {"user_id": 3, "status": "pending", "order_date": datetime.now() - timedelta(days=5)},
            {"user_id": 1, "status": "completed", "order_date": datetime.now() - timedelta(days=3)},
            {"user_id": 4, "status": "completed", "order_date": datetime.now() - timedelta(days=2)},
            {"user_id": 5, "status": "pending", "order_date": datetime.now() - timedelta(days=1)},
        ]
        
        for order_data in orders_data:
            order = Order(**order_data, total_amount=0)  # Will calculate total later
            db.add(order)
        db.commit()
        
        # Create sample order items
        order_items_data = [
            {"order_id": 1, "product_id": 1, "quantity": 1, "price": 999.99},
            {"order_id": 1, "product_id": 3, "quantity": 1, "price": 199.99},
            {"order_id": 2, "product_id": 2, "quantity": 1, "price": 699.99},
            {"order_id": 2, "product_id": 4, "quantity": 2, "price": 39.99},
            {"order_id": 3, "product_id": 6, "quantity": 1, "price": 299.99},
            {"order_id": 4, "product_id": 5, "quantity": 3, "price": 12.99},
            {"order_id": 4, "product_id": 8, "quantity": 1, "price": 89.99},
            {"order_id": 5, "product_id": 7, "quantity": 1, "price": 349.99},
            {"order_id": 6, "product_id": 1, "quantity": 1, "price": 999.99},
            {"order_id": 6, "product_id": 2, "quantity": 1, "price": 699.99},
        ]
        
        for item_data in order_items_data:
            order_item = OrderItem(**item_data)
            db.add(order_item)
        db.commit()
        
        # Update order totals
        orders = db.query(Order).all()
        for order in orders:
            total = sum(item.quantity * item.price for item in order.order_items)
            order.total_amount = total
        db.commit()
        
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    create_sample_data() 