import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set page config for a centered layout and baseball favicon
st.set_page_config(page_title="Umpire GPT", page_icon="⚾", layout="centered")

# Custom CSS for horizontal selectbox
st.markdown("""
    <style>
    .stSelectbox {
        display: inline-block;
        width: auto !important;
    }
    .stSelectbox > div > div {
        display: flex;
        flex-direction: row;
        align-items: center;
    }
    .stSelectbox label {
        font-size: 16px;
        font-weight: bold;
        margin-right: 10px;
    }
    .stSelectbox select {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for chat history and division
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "division" not in st.session_state:
    st.session_state.division = "No Filters"

# Horizontal layout for division selection
col1, _ = st.columns([2, 3])
with col1:
    division = st.selectbox(
        "Select your division",
        ["No Filters", "Rookie A (7U)", "Rookie AA (8U)", "Supreme A (9U-10U)", "Supreme AA (9U-10U)", "Majors A (11U-12U)", "Majors AA (11U-12U)", "Juniors (13U-14U)"],
        index=0,  # Default to No Filters
        help="Choose the Naperville Little League division for rule-specific answers."
    )
    st.session_state.division = division

# Header
st.title("Umpire GPT")
st.write(f"Ask a baseball question or describe a scenario (Division: {st.session_state.division}).")

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
            # Include division in the prompt
            prompt = f"Division: {st.session_state.division}\nPrevious conversation:\n{context}\n\nCurrent question: {question}"
            # Set up retry logic
            session = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
            session.mount('https://', HTTPAdapter(max_retries=retries))
            # Use /validate_call for scenario-based questions, /query otherwise
            endpoint = "/validate_call" if "umpire" in question.lower() or "call" in question.lower() else "/query"
            response = session.get(
                f"https://umpiregpt-v1-543806448733.us-central1.run.app{endpoint}",
                params={"question": prompt},
                timeout=30
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
