import streamlit as st
import requests

st.title("UmpireGPT: Little League Rulebook Assistant")
st.write("Ask questions about Little League rules and get answers based on the Official Little League Rulebook.")
question = st.text_input("Enter your question:")
if st.button("Submit"):
    if question:
        response = requests.get(f"https://umpiregpt-v1-qovl4xndza-uc.a.run.app/query?question={question}")
        if response.status_code == 200:
            result = response.json()
            st.write(f"**Question:** {result['question']}")
            st.write(f"**Answer:** {result['answer']}")
        else:
            st.error(f"Error fetching response: {response.status_code}")
