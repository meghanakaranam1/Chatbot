import streamlit as st
import requests
import json

st.title("🔧 Chatbot Debug Test")

# Simple test
st.write("Testing backend connection...")

try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        st.success("✅ Backend is connected!")
        st.json(response.json())
    else:
        st.error(f"❌ Backend error: {response.status_code}")
except Exception as e:
    st.error(f"❌ Connection failed: {e}")

st.divider()

# Simple chat test
st.write("Testing chat functionality...")

if st.button("Test Query: How many users?"):
    with st.spinner("Sending request..."):
        try:
            payload = {"message": "How many users do we have?"}
            response = requests.post(
                "http://localhost:8000/chat/",
                json=payload,
                timeout=10
            )
            
            st.write("**Response Status:**", response.status_code)
            st.write("**Raw Response:**")
            st.json(response.json())
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Chat is working!")
                st.write("**Bot Response:**", data.get("response", "No response"))
                if data.get("data"):
                    st.write("**Data:**")
                    st.json(data["data"])
            else:
                st.error("❌ Chat failed")
                
        except Exception as e:
            st.error(f"❌ Chat request failed: {e}")

st.divider()

# Manual input test
st.write("Manual test:")
user_input = st.text_input("Enter your question:")
if st.button("Send Manual Test") and user_input:
    try:
        payload = {"message": user_input}
        response = requests.post(
            "http://localhost:8000/chat/",
            json=payload,
            timeout=10
        )
        
        st.write("**Status:**", response.status_code)
        st.json(response.json())
        
    except Exception as e:
        st.error(f"Error: {e}") 