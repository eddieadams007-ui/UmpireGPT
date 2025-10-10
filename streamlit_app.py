import streamlit as st
import requests
import os
from datetime import datetime

# Backend API URL (from environment variable, defaults to production)
API_URL = os.getenv("API_URL", "https://umpiregpt-production-543806448733.us-central1.run.app")

# App title with version badge (dev or production)
VERSION = os.getenv("APP_VERSION", "v1.0 Beta")
st.set_page_config(page_title=f"UmpGPT {VERSION} - Little League Rules Chat", page_icon="⚾", layout="wide")

st.title(f"⚾ UmpGPT {VERSION}")
st.sidebar.title(f"UmpGPT {VERSION}")
st.sidebar.markdown("**Little League Rules Chat** - Ask about rules or validate calls.")

# Show backend URL for debugging (hide in production if needed)
if "dev" in VERSION.lower():
    st.sidebar.markdown(f"**Backend**: {API_URL} (Dev Mode)")

# Division selector
division = st.sidebar.selectbox("Select Division", ["Majors A", "Majors B", "Minors", "Tee Ball", "No Filters"])

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a rule question or validate a call (e.g., 'With two outs and runner on first, dropped third strike?')"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare query with division
    question = f"Division: {division}\n{prompt}" if division != "No Filters" else prompt

    # Call backend API
    with st.chat_message("assistant"):
        with st.spinner("Umpiring the call..."):
            try:
                response = requests.get(f"{API_URL}/query", params={"question": question, "thumbs_up": 0, "thumbs_down": 0, "feedback_text": ""})
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    # Feedback buttons
                    col1, col2, col3 = st.columns([1, 1, 6])
                    with col1:
                        if st.button("👍 Great"):
                            requests.get(f"{API_URL}/query", params={"question": question, "thumbs_up": 1, "thumbs_down": 0, "feedback_text": "Great response!"})
                            st.success("Thanks—logged! 👍")
                    with col2:
                        if st.button("👎 Not helpful"):
                            requests.get(f"{API_URL}/query", params={"question": question, "thumbs_up": 0, "thumbs_down": 1, "feedback_text": "Not helpful"})
                            st.warning("Sorry—logged for improvement. 👎")
                    with col3:
                        feedback = st.text_input("Additional feedback (optional)")
                        if st.button("Submit Feedback") and feedback:
                            requests.get(f"{API_URL}/query", params={"question": question, "thumbs_up": 0, "thumbs_down": 0, "feedback_text": feedback})
                            st.success("Feedback submitted—thanks for helping UmpGPT improve!")
                else:
                    st.error(f"API error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown(f"**UmpGPT {VERSION}** - Powered by Little League Rulebook + OpenAI")
st.sidebar.markdown("**Feedback?** Email eddie@umpiregpt.com")
