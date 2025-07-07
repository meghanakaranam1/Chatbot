from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db, init_database
from database.seed_data import create_sample_data
from backend import crud, schemas
from config import FASTAPI_HOST, FASTAPI_PORT

app = FastAPI(title="Chatbot API", description="AI Chatbot with Database Integration", version="1.0.0")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_database()
        # Check if data exists, if not create sample data
        db = next(get_db())
        users = crud.get_users(db, limit=1)
        if not users:
            create_sample_data()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.get("/")
async def root():
    return {"message": "Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# User endpoints
@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# Product endpoints
@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.get("/products/category/{category}", response_model=List[schemas.Product])
def read_products_by_category(category: str, db: Session = Depends(get_db)):
    products = crud.get_products_by_category(db, category=category)
    return products

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

# Order endpoints
@app.get("/orders/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders

@app.get("/orders/user/{user_id}", response_model=List[schemas.Order])
def read_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_user(db, user_id=user_id)
    return orders

@app.get("/orders/status/{status}", response_model=List[schemas.Order])
def read_orders_by_status(status: str, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_status(db, status=status)
    return orders

# Database schema endpoint
@app.get("/schema/")
def get_schema(db: Session = Depends(get_db)):
    """Get database schema for LLM context"""
    return crud.get_database_schema(db)

# Raw SQL query endpoint (for testing)
@app.post("/query/")
def execute_query(query: str, db: Session = Depends(get_db)):
    """Execute raw SQL query - for testing purposes"""
    try:
        results = crud.execute_sql_query(db, query)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Chat endpoints
@app.post("/chat/", response_model=schemas.ChatResponse)
def chat_with_bot(message: schemas.ChatMessage, db: Session = Depends(get_db)):
    """Main chat endpoint that processes natural language queries"""
    from backend.llm_service import llm_service
    
    try:
        # Process the natural language query
        result = llm_service.process_natural_language_query(message.message, db)
        
        if result["success"]:
            return schemas.ChatResponse(
                response=result["explanation"],
                data=result["results"],
                query_type="database_query"
            )
        else:
            return schemas.ChatResponse(
                response=result["explanation"],
                data=[],
                query_type="error"
            )
    except Exception as e:
        return schemas.ChatResponse(
            response=f"I'm sorry, I encountered an error: {str(e)}",
            data=[],
            query_type="error"
        )

@app.post("/chat/query/", response_model=schemas.QueryResponse)
def process_natural_language_query(request: schemas.QueryRequest, db: Session = Depends(get_db)):
    """Process natural language query and return detailed results"""
    from backend.llm_service import llm_service
    
    try:
        result = llm_service.process_natural_language_query(request.natural_language_query, db)
        
        return schemas.QueryResponse(
            sql_query=result["sql_query"],
            results=result["results"],
            explanation=result["explanation"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/chat/examples/")
def get_query_examples():
    """Get example queries that users can try"""
    examples = [
        "How many users do we have?",
        "Show me all products in the Electronics category",
        "What's the total revenue from completed orders?",
        "Which are the most expensive products?",
        "Show me recent orders",
        "How many pending orders are there?",
        "What are the best selling products?",
        "Show me users by city",
        "How many products are in each category?"
    ]
    
    return {"examples": examples}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT) 