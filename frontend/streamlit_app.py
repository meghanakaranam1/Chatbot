import streamlit as st
import requests
import pandas as pd
import json
from typing import Dict, List, Any
import time

# Configuration
try:
    from deployment_config import config
    API_BASE_URL = config.API_BASE_URL
except ImportError:
    API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Alo-Veda",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .chat-message {
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 12px;
        border-left: 4px solid;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background-color: #F8F9FA;
        border-left-color: #1976D2;
        margin-left: 2rem;
        color: #212529;
    }
    
    .user-message strong {
        color: #1976D2;
        font-weight: 600;
    }
    
    .bot-message {
        background-color: #E8F5E8;
        border-left-color: #2E7D32;
        margin-right: 2rem;
        color: #1B5E20;
    }
    
    .bot-message strong {
        color: #2E7D32;
        font-weight: 600;
    }
    
    .example-query {
        background-color: #FFFFFF;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        cursor: pointer;
        border: 2px solid #E0E0E0;
        color: #424242;
        transition: all 0.2s ease;
    }
    
    .example-query:hover {
        background-color: #F5F5F5;
        border-color: #2E7D32;
        color: #1B5E20;
    }
    
    /* Improve sidebar styling */
    .css-1d391kg {
        background-color: #FAFAFA;
    }
    
    /* Make dataframes more readable */
    .dataframe {
        background-color: #FFFFFF !important;
        color: #212529 !important;
    }
    
    /* Improve code blocks */
    .stCodeBlock {
        background-color: #F8F9FA !important;
        border: 1px solid #E0E0E0 !important;
    }
    
    /* Better button styling */
    .stButton > button {
        background-color: #2E7D32;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: background-color 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #1B5E20;
        color: white;
    }
    
    /* Fix text input styling */
    .stTextInput > div > div > input {
        background-color: #FFFFFF;
        color: #212529;
        border: 2px solid #E0E0E0;
        border-radius: 6px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2E7D32;
        box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.2);
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_query_examples():
    """Get example queries from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/chat/examples/")
        if response.status_code == 200:
            return response.json()["examples"]
    except:
        pass
    
    # Fallback examples
    return [
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

def send_chat_message(message: str) -> Dict[str, Any]:
    """Send a message to the chatbot API"""
    try:
        payload = {"message": message}
        response = requests.post(
            f"{API_BASE_URL}/chat/",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"Error: API returned status code {response.status_code}",
                "data": [],
                "query_type": "error"
            }
    except requests.exceptions.Timeout:
        return {
            "response": "Request timed out. Please try again.",
            "data": [],
            "query_type": "error"
        }
    except Exception as e:
        return {
            "response": f"Connection error: {str(e)}",
            "data": [],
            "query_type": "error"
        }

def format_data_for_display(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Format API response data for display"""
    if not data:
        return pd.DataFrame()
    
    return pd.DataFrame(data)

def main():
    # Header
    st.markdown("<h1 class='main-header'>🤖 Alo-Veda</h1>", unsafe_allow_html=True)
    st.markdown("Ask questions about your database in natural language!")
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ Backend API is not running. Please start the FastAPI server first.")
        st.code("python backend/main.py")
        return
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar with examples and info
    with st.sidebar:
        st.header("📚 Example Queries")
        st.markdown("Click on any example to try it:")
        
        examples = get_query_examples()
        for i, example in enumerate(examples):
            if st.button(example, key=f"example_{i}"):
                # Process the example query directly
                process_query(example)
        
        st.divider()
        
        st.header("ℹ️ How to Use")
        st.markdown("""
        1. Type your question in natural language
        2. The AI will convert it to SQL
        3. Results will be displayed in a table
        4. You can also see the generated SQL query
        """)
        
        st.header("📊 Database Schema")
        with st.expander("View Tables"):
            st.markdown("""
            - **Users**: Customer information
            - **Products**: Product catalog
            - **Orders**: Order records
            - **Order Items**: Individual order details
            """)
    
    # Chat interface
    st.header("💬 Alo-Veda")
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>Bot:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Display data if available
            if "data" in message and message["data"]:
                df = format_data_for_display(message["data"])
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
            
            # Display SQL query if available
            if "sql_query" in message and message["sql_query"]:
                with st.expander("🔍 View Generated SQL"):
                    st.code(message["sql_query"], language="sql")
    
    # Input form - using form to handle submission better
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Ask a question about your database:",
            placeholder="e.g., How many users do we have?"
        )
        submitted = st.form_submit_button("Send", type="primary")
    
    # Process user input
    if submitted and user_input.strip():
        process_query(user_input.strip())
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Chat", help="Clear all messages"):
            st.session_state.messages = []
            st.rerun()

def process_query(user_input: str):
    """Process a user query and update the chat"""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Show loading spinner
    with st.spinner("🔄 Processing your query..."):
        # Send message to API
        response = send_chat_message(user_input)
        
        # Add bot response to chat
        bot_message = {
            "role": "bot",
            "content": response["response"],
            "data": response.get("data", []),
            "query_type": response.get("query_type", "")
        }
        
        # If we have query details, add SQL query to the message
        if response.get("data"):
            try:
                detailed_response = requests.post(
                    f"{API_BASE_URL}/chat/query/",
                    json={"natural_language_query": user_input},
                    timeout=30
                )
                if detailed_response.status_code == 200:
                    details = detailed_response.json()
                    bot_message["sql_query"] = details.get("sql_query", "")
            except:
                pass
        
        st.session_state.messages.append(bot_message)
    
    # Force refresh
    st.rerun()

if __name__ == "__main__":
    main() 