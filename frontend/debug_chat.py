import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Debug Chat Test",
    page_icon="🐛",
    layout="wide"
)

API_BASE_URL = "http://localhost:8000"

def test_api():
    """Test if API is working"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(message):
    """Send message to API and return response"""
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
            return {"error": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

st.title("🐛 Debug Chat Test")

# Test API connection
if test_api():
    st.success("✅ API is connected")
else:
    st.error("❌ API is not connected")
    st.stop()

# Simple input and response
user_input = st.text_input("Enter your question:")

if st.button("Send") and user_input:
    st.write("**You asked:**", user_input)
    
    with st.spinner("Processing..."):
        response = send_message(user_input)
    
    st.write("**Raw API Response:**")
    st.json(response)
    
    if "response" in response:
        st.write("**Bot Response:**", response["response"])
    
    if "data" in response and response["data"]:
        st.write("**Data:**")
        st.dataframe(response["data"])

# Test with a fixed query
st.divider()
st.subheader("Quick Test")

if st.button("Test: 'What products do we have?'"):
    test_response = send_message("What products do we have?")
    st.json(test_response) 