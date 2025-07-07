# 🤖 AI Database Chatbot

A powerful chatbot that allows you to query your database using natural language, powered by FastAPI, Streamlit, and Large Language Models.

## ✨ Features

- **Natural Language Queries**: Ask questions about your database in plain English
- **AI-Powered SQL Generation**: Converts natural language to SQL queries automatically
- **Interactive Web Interface**: Beautiful Streamlit frontend with chat interface
- **Real-time Results**: Get instant responses with formatted data tables
- **Query Transparency**: View the generated SQL queries for learning
- **Example Queries**: Pre-built examples to get you started quickly
- **RESTful API**: Complete FastAPI backend with full documentation

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐    SQL    ┌─────────────┐
│   Streamlit     │ ────────────── │    FastAPI      │ ───────── │   SQLite    │
│   Frontend      │                │    Backend      │           │  Database   │
└─────────────────┘                └─────────────────┘           └─────────────┘
                                            │
                                            │
                                    ┌─────────────────┐
                                    │   LLM Service   │
                                    │ (NL to SQL)     │
                                    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- 4GB+ RAM (for LLM models)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd Chatbot
```

### 2. Choose Installation Method

**Option A: Minimal Install (Recommended for getting started)**
```bash
pip install -r requirements.txt
```
This installs core functionality with rule-based SQL generation.

**Option B: Full AI Install (Enhanced features)**
```bash
pip install -r requirements-full.txt
```
This includes ML models for advanced natural language processing.

**Option C: Manual Minimal Install (if you have dependency issues)**
```bash
pip install fastapi uvicorn streamlit sqlalchemy pydantic requests pandas python-multipart
```

### 3. Start the Application

**Option A: Start everything at once**
```bash
python start_chatbot.py
```

**Option B: Start services separately**

Terminal 1 (Backend):
```bash
python run_backend.py
```

Terminal 2 (Frontend):
```bash
python run_frontend.py
```

### 4. Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Usage

### Example Queries

Try these natural language queries:

- "How many users do we have?"
- "Show me all products in the Electronics category"
- "What's the total revenue from completed orders?"
- "Which are the most expensive products?"
- "Show me recent orders"
- "How many pending orders are there?"
- "What are the best selling products?"
- "Show me users by city"
- "How many products are in each category?"

### Using the Web Interface

1. Open your browser to http://localhost:8501
2. Type your question in natural language
3. Click "Send" or press Enter
4. View the results in a formatted table
5. Expand "View Generated SQL" to see the SQL query

### Using the API Directly

```python
import requests

# Send a chat message
response = requests.post(
    "http://localhost:8000/chat/",
    json={"message": "How many users do we have?"}
)

print(response.json())
```

## 📊 Database Schema

The chatbot comes with a pre-populated sample database:

### Tables

- **users**: Customer information (id, name, email, age, city, created_at)
- **products**: Product catalog (id, name, description, price, category, stock_quantity, created_at)
- **orders**: Order records (id, user_id, total_amount, status, order_date)
- **order_items**: Individual order details (id, order_id, product_id, quantity, price)

### Sample Data

- 5 users from different cities
- 8 products across multiple categories
- 6 orders with various statuses
- 10 order items linking orders to products

## 🔧 Configuration

Edit `config.py` to customize settings:

```python
# Database configuration
DATABASE_URL = "sqlite:///./database/chatbot.db"

# API configuration
FASTAPI_HOST = "localhost"
FASTAPI_PORT = 8000

# Streamlit configuration  
STREAMLIT_PORT = 8501

# Model configuration
LLAMA_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
MAX_TOKENS = 512
TEMPERATURE = 0.7
```

## 🛠️ Development

### Project Structure

```
Chatbot/
├── backend/              # FastAPI backend
│   ├── __init__.py
│   ├── main.py          # Main API application
│   ├── schemas.py       # Pydantic models
│   ├── crud.py          # Database operations
│   └── llm_service.py   # LLM integration
├── frontend/            # Streamlit frontend
│   └── streamlit_app.py # Main UI application
├── database/            # Database components
│   ├── __init__.py
│   ├── models.py        # SQLAlchemy models
│   ├── database.py      # Database connection
│   └── seed_data.py     # Sample data
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── run_backend.py       # Backend startup script
├── run_frontend.py      # Frontend startup script
├── start_chatbot.py     # Combined startup script
└── README.md           # This file
```

### Adding New Tables

1. Define model in `database/models.py`
2. Update schema info in `backend/crud.py`
3. Add sample data in `database/seed_data.py`
4. Update LLM patterns in `backend/llm_service.py`

### Customizing the LLM

The system uses a hybrid approach:
- Rule-based patterns for common queries
- CodeT5 model for complex SQL generation
- Fallback to rule-based system if model fails

To use a different model, update `backend/llm_service.py`:

```python
# Change model in LLMService.__init__()
self.tokenizer = AutoTokenizer.from_pretrained("your-model-name")
self.model = AutoModelForCausalLM.from_pretrained("your-model-name")
```

## 📚 API Documentation

### Main Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /chat/` - Main chat endpoint
- `POST /chat/query/` - Detailed query processing
- `GET /chat/examples/` - Get example queries
- `GET /schema/` - Get database schema

### Example API Usage

```python
import requests

# Health check
health = requests.get("http://localhost:8000/health")
print(health.json())

# Send a chat message
chat_response = requests.post(
    "http://localhost:8000/chat/",
    json={"message": "Show me all users"}
)
print(chat_response.json())

# Get detailed query information
query_response = requests.post(
    "http://localhost:8000/chat/query/",
    json={"natural_language_query": "How many products are there?"}
)
print(query_response.json())
```

## 🚨 Troubleshooting

### Common Issues

**Installation Issues (Python 3.13+)**
- Use minimal install: `pip install -r requirements.txt`
- If still failing, try manual install: `pip install fastapi uvicorn streamlit sqlalchemy pydantic requests pandas python-multipart`
- Consider using Python 3.11 or 3.12 for better compatibility

**Backend won't start**
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

**Frontend can't connect to backend**
- Ensure backend is running on http://localhost:8000
- Check firewall settings

**LLM model fails to load**
- The system will fallback to rule-based SQL generation
- Check available memory (models require 4GB+)
- Verify internet connection for model download

**Database errors**
- Delete the database file and restart: `rm database/chatbot.db`
- The system will recreate it automatically

### Getting Help

- Check the console output for error messages
- Visit http://localhost:8000/docs for API documentation
- Ensure all requirements are installed correctly

## 🔒 Security Notes

- This is a development setup with CORS enabled for all origins
- In production, restrict CORS origins and add authentication
- SQL injection is mitigated by using SQLAlchemy ORM
- Consider rate limiting for production deployments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [Streamlit](https://streamlit.io/)
- AI capabilities via [Transformers](https://huggingface.co/transformers/)
- Database handling with [SQLAlchemy](https://sqlalchemy.org/)

---

**Happy Chatting! 🎉** 