from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables"""
    create_tables()
    print("Database initialized successfully!") 