import streamlit as st
import requests
import time

# Set page config for a centered layout and baseball favicon
st.set_page_config(page_title="UmpireGPT", page_icon="⚾", layout="centered")

# Custom CSS for styling and text wrapping
st.markdown(
    """
    <style>
    .main {background-color: #f5f5f5;}
    .stTextArea > div > div > textarea {
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
    </style>
    """,
    unsafe_allow_html=True
)

# JavaScript to submit on single Return key (not Shift+Return)
st.markdown(
    """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const textarea = document.querySelector('textarea');
        textarea.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey && !event.altKey) {
                event.preventDefault();
                const button = document.querySelector('button[kind="secondary"]');
                if (button) button.click();
            }
        });
    });
    </script>
    """,
    unsafe_allow_html=True
)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("UmpireGPT")
st.markdown("Ask a baseball question or describe a scenario. Keep asking follow-up questions to dive deeper.")

# Display chat history
if st.session_state.chat_history:
    st.subheader("Conversation History")
    for msg in reversed(st.session_state.chat_history[-5:]):
        st.markdown(f"<div class='chat-message user'>You: {msg['question']}</div>", unsafe_allow_html=True)
        placeholder = st.empty()
        answer = msg['answer']
        if not msg.get('displayed', False):
            displayed_text = ""
            for char in answer:
                displayed_text += char
                placeholder.markdown(f"<div class='chat-message bot'>UmpireGPT: {displayed_text}</div>", unsafe_allow_html=True)
                time.sleep(0.01)  # Adjust speed for typing effect
            msg['displayed'] = True
        else:
            placeholder.markdown(f"<div class='chat-message bot'>UmpireGPT: {answer}</div>", unsafe_allow_html=True)

# Chat input
question = st.text_area("Your question:", placeholder="e.g., What is a balk?", height=100, key="question_input", clear_on_submit=True)

# Go button
if st.button("Go", key="go_button"):
    if question:
        with st.spinner("Checking the rulebook..."):
            try:
                # Build context from last 3 messages
                context = "\n".join(
                    [f"Q: {msg['question']}\nA: {msg['answer']}" 
                     for msg in st.session_state.chat_history[-3:]]
                )
                prompt = f"Previous conversation:\n{context}\n\nCurrent question: {question}"
                response = requests.get(
                    f"https://umpiregpt-v1-qovl4xndza-uc.a.run.app/query?question={prompt}",
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": result["answer"],
                    "displayed": False
                })
                st.rerun()  # Refresh to show new message
            except requests.RequestException as e:
                st.error(f"Uh-oh! Couldn't reach the server: {str(e)}. Try again!")
    else:
        st.warning("Please enter a question!")
