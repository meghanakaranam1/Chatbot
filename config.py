# Configuration settings for the chatbot
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/chatbot.db")

# API configuration
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "localhost")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

# Streamlit configuration
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# Model configuration
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
MODEL_NAME = os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")

# LLaMA model configuration
LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME", "meta-llama/Llama-2-7b-chat-hf")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7")) 