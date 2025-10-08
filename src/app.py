import streamlit as st
import requests

# Set page config for a centered layout and baseball favicon
st.set_page_config(page_title="Umpire GPT", page_icon="⚾", layout="centered")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("Umpire GPT")
st.write("Ask a baseball question or describe a scenario.")

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(msg["question"])
    with st.chat_message("assistant"):
        st.markdown(msg["answer"])

# Chat input
question = st.chat_input(placeholder="What do you want to know?")

# Handle submission
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
                "https://umpiregpt-v1-qovl4xndza-uc.a.run.app/query",
                params={"question": prompt},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            if not result.get("answer"):
                st.error("Received an empty response from the server. Please try again.")
            else:
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": result["answer"]
                })
                st.rerun()
        except requests.RequestException as e:
            st.error(f"Error: Couldn't reach the server ({str(e)}). Try again!")
        except ValueError as e:
            st.error(f"Error: Invalid response format ({str(e)}). Try again!")
