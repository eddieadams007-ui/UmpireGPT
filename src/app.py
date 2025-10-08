import streamlit as st
import requests
import json

# Set page config for a wider layout and baseball favicon
st.set_page_config(page_title="UmpireGPT", page_icon="⚾", layout="centered")

# Custom CSS for chat-like styling
st.markdown(
    """
    <style>
    .main {background-color: #f5f5f5;}
    .stTextInput > div > div > input {border-radius: 10px; padding: 10px; font-size: 16px;}
    .stButton > button {background-color: #4CAF50; color: white; border-radius: 10px; font-size: 16px; padding: 10px 20px;}
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

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Header with baseball theme
st.title("⚾ UmpireGPT: Your Little League Rulebook Buddy")
st.markdown(
    "Hey there, coach, ump, or player! Ask me anything about Little League rules, and I’ll explain it like we’re chatting on the diamond. Keep asking follow-up questions to dive deeper!"
)

# Example questions to guide users
with st.expander("Need ideas? Try these!"):
    st.write("- What is the strike zone in Little League?")
    st.write("- Can a runner steal home in Little League?")
    st.write("- What is a balk in Little League?")
    st.write("- What happens to runners after a balk?")

# Chat input
question = st.text_input("What's your question?", placeholder="e.g., What is a balk?", key="question_input")

# Submit button
if st.button("Ask Away!"):
    if question:
        with st.spinner("Checking the rulebook..."):
            try:
                # Build context from last 3 messages for conversational continuity
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
                        "answer": result["answer"]
                    })
                else:
                    st.error(f"Oops! Something went wrong (Error {response.status_code}). Try again or ask something else!")
            except requests.RequestException as e:
                st.error(f"Uh-oh! Couldn't reach the server: {str(e)}. Check your connection and try again!")
    else:
        st.warning("Please enter a question to get an answer!")

# Display chat history
if st.session_state.chat_history:
    st.subheader("Our Chat")
    for i, msg in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
        st.markdown(f"<div class='chat-message user'>You: {msg['question']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-message bot'>UmpireGPT: {msg['answer']}</div>", unsafe_allow_html=True)
