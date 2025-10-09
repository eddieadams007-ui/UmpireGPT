import os
from openai import OpenAI

class RAG:
    def __init__(self, data_path, index_path, meta):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.data_path = data_path
        self.index_path = index_path
        self.meta = meta

    def generate_answer(self, question, context, idmap):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Question: {question}\nContext: {context}"}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DEBUG: Failed to generate answer: {e}")
            raise

    def classify_intent(self, question):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"""
Classify the intent of this question as 'rule_clarification', 'scenario_based', or 'other'.
- 'rule_clarification': Questions asking for general rule explanations (e.g., 'What is the dropped third strike rule?').
- 'scenario_based': Questions describing specific game situations with details like outs, runners, or umpire calls (e.g., 'With two outs and a runner on first, is the call correct?').
- 'other': Non-rule questions (e.g., 'What is the time limit for a game?').
Return only the intent name.
Question: {question}
"""
                }]
            )
            intent = response.choices[0].message.content.strip().lower()
            return intent if intent in ['rule_clarification', 'scenario_based', 'other'] else 'other'
        except Exception as e:
            print(f"DEBUG: Failed to classify intent: {e}")
            return 'other'

    def check_scenario_slots(self, question):
        required_slots = ['outs', 'runners', 'call_made']
        present_slots = []
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in ['out ', 'outs ', 'no outs', 'one out', 'two outs']):
            present_slots.append('outs')
        if any(keyword in question_lower for keyword in ['runner', 'runners', 'on first', 'on second', 'on third', 'bases loaded', 'base']):
            present_slots.append('runners')
        if any(keyword in question_lower for keyword in ['call ', 'umpire', 'correct', 'right', 'wrong', 'called']):
            present_slots.append('call_made')
        missing_slots = [slot for slot in required_slots if slot not in present_slots]
        return missing_slots
