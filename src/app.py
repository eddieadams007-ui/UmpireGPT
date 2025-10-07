import streamlit as st
   import requests

   st.title("UmpireGPT: Little League Rulebook Assistant")
   st.write("Ask questions about Little League rules and get answers based on the Official Little League Rulebook.")
   question = st.text_input("Enter your question:")
   if st.button("Submit"):
       if question:
           # Use localhost for containerized FastAPI backend
           response = requests.get(f"http://localhost:8000/query?question={question}")
           if response.status_code == 200:
               result = response.json()
               st.write(f"**Question:** {result['question']}")
               st.write(f"**Answer:** {result['answer']}")
           else:
               st.error(f"Error fetching response: {response.status_code}")
