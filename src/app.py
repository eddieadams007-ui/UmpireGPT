import streamlit as st
import requests
import time
import json

# Set page config for a centered layout and baseball favicon
st.set_page_config(page_title="UmpireGPT", page_icon="⚾", layout="centered")

# Custom CSS for styling and text wrapping
st.markdown(
    """
    <style>
    .main {background-color: #f5f5f5;}
    .stTextInput > div > div > textarea {
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        resize: vertical;
        white-space: pre-wrap;
        word-wrap: break-word;
        height: 100px;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        font-size: 16px;
        padding: 10px 20px;
    }
    .stButton > button:hover {background-color: #45a049;}
    .chat-message {padding: 10px; margin: 5px; border-radius: 10px; font-size: 14px;}
    .user {background-color: #e6f3ff; text-align: right; margin-left: 20%;}
    .bot {background-color: #f0f0f0; margin-right: 20%;}
    .question {font-weight: bold; color: #2c3e50;}
    .answer {color: #34495e; line-height: 1.6;}
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for current chat and saved chats
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = 0

# Header
st.title("UmpireGPT")
st.markdown("Ask a baseball question or describe a scenario. Keep asking follow-up questions to dive deeper.")

# Saved chats dropdown
saved_chat_options = ["New Chat"] + [f"Chat {i+1}" for i, _ in enumerate(st.session_state.saved_chats)]
selected_chat = st.selectbox("Select a chat:", saved_chat_options, key="chat_selector")

# Handle chat selection
if selected_chat != "New Chat":
    chat_index = int(selected_chat.split(" ")[1]) - 1
    st.session_state.chat_history = st.session_state.saved_chats[chat_index]
    st.session_state.current_chat_id = chat_index + 1
else:
    if st.session_state.chat_history and st.session_state.current_chat_id == len(st.session_state.saved_chats):
        st.session_state.saved_chats.append(st.session_state.chat_history.copy())
    st.session_state.chat_history = []
    st.session_state.current_chat_id = len(st.session_state.saved_chats) + 1

# New Chat button
if st.button("New Chat"):
    if st.session_state.chat_history:
        st.session_state.saved_chats.append(st.session_state.chat_history.copy())
    st.session_state.chat_history = []
    st.session_state.current_chat_id = len(st.session_state.saved_chats) + 1
    st.rerun()

# Display chat history
if st.session_state.chat_history:
    st.subheader("Conversation History")
    for i, msg in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
        st.markdown(f"<div class='chat-message user'>You: {msg['question']}</div>", unsafe_allow_html=True)
        # Placeholder for typing effect
        placeholder = st.empty()
        answer = msg['answer']
        # Simulate typing only for new messages
        if not msg.get('displayed', False):
            displayed_text = ""
            for char in answer:
                displayed_text += char
                placeholder.markdown(f"<div class='chat-message bot'>UmpireGPT: {displayed_text}</div>", unsafe_allow_html=True)
                time.sleep(0.01)  # Adjust speed for typing effect
            msg['displayed'] = True
        else:
            placeholder.markdown(f"<div class='chat-message bot'>UmpireGPT: {answer}</div>", unsafe_allow_html=True)

# Chat input at the bottom
with st.form(key="question_form", clear_on_submit=True):
    question = st.text_area("Your question:", placeholder="e.g., What is a balk?", height=100)
    submit_button = st.form_submit_button("Go")

# Handle form submission
if submit_button and question:
    with st.spinner("Checking the rulebook..."):
        try:
            # Build context from last 3 messages
            context = "\n".join(
                [f"Q: {msg['question']}\nA: {msg['answer']}" 
                 for msg in st.session_state.chat_history[-3:]]
            )
            prompt = f"Previous conversation:\n{context}\n\nCurrent question: {question}"
            response = requests.get(
                f"https://umpiregpt-v1-qovl4xndza-uc.a.run.app/query?question={prompt}"
            )
            if response.status_code == 200:
                result = response.json()
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": result["answer"],
                    "displayed": False
                })
            else:
                st.error(f"Oops! Something went wrong (Error {response.status_code}). Try again!")
        except requests.RequestException as e:
            st.error(f"Uh-oh! Couldn't reach the server: {str(e)}. Check your connection and try again!")
elif submit_button and not question:
    st.warning("Please enter a question!")
