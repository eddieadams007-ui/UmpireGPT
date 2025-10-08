import os
import json
from .config import OPENAI_API_KEY, USE_OPENAI
from openai import OpenAI

class RAG:
    def __init__(self, data_path, index_path, meta):
        self.data_path = data_path
        self.index_path = index_path
        self.meta = meta
        self.client = OpenAI(api_key=OPENAI_API_KEY) if USE_OPENAI else None

    def classify_intent(self, query):
        """Classify the intent of the query using gpt-4o-mini."""
        if not self.client:
            return "rule_reference"  # Fallback if no OpenAI client
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a baseball coach classifying user questions into one of these intents: 'scenario_based' (describes a game situation needing outs/base state), 'rule_reference' (asks for specific rule), 'philosophical' (asks why a rule exists), 'opinion' (asks for stories or opinions), 'off_topic' (unrelated to baseball rules). Respond with only the intent name."},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "rule_reference"  # Fallback on error

    def check_scenario_slots(self, query):
        """Check if scenario-based question has required slots (outs, base state)."""
        required_slots = ["outs", "base state"]
        missing_slots = []
        for slot in required_slots:
            if slot not in query.lower():
                missing_slots.append(slot)
        return missing_slots

    def generate_answer(self, query, context, idmap):
        if not context:
            return "Hey there! I couldn't find any relevant rules in the rulebook for that one. Can you clarify or ask something else?"
        if not os.path.exists(self.data_path) or not os.path.exists(self.index_path):
            return "Oops, something went wrong—couldn't find the rulebook data. Let's try another question!"
        context_with_ids = []
        for doc in context:
            doc_id = idmap.get(list(idmap.index).index(int(doc['id'].split('_')[-1]) if 'doc_' in doc['id'] else int(doc['id'])), doc['id'])
            context_with_ids.append(f"Rule ID: {doc_id}, Text: {doc['text']}")
        context_text = " ".join(context_with_ids)
        intent = self.classify_intent(query)
        if intent == "scenario_based":
            missing_slots = self.check_scenario_slots(query)
            if missing_slots:
                return f"Hey coach, I need a bit more info to nail this call! Can you tell me about {', '.join(missing_slots)}? For example, how many outs are there, and who's on base?"
        system_prompt = (
            "You're a friendly baseball coach answering questions based on the Official Baseball Rulebook. "
            "Use a clear, conversational tone, as if explaining to a player, parent, or volunteer coach. "
            "Be enthusiastic, use baseball lingo when appropriate, and make it feel like we're chatting on the diamond! "
            "Always prioritize fairness, safety, and player development. "
            "If the question is a rule lookup, cite the rule number and paraphrase. "
            "For philosophical questions, explain the rule's purpose in plain language with citations. "
            "For opinion or storytelling, use teaching examples or admit if it's outside the rulebook. "
            "For off-topic questions, politely redirect to baseball rules or say it's not covered."
        )
        if intent == "rule_reference":
            prompt = (
                f"{system_prompt}\n\n"
                f"Here's the relevant rulebook context: {context_text}\n\n"
                f"Question: {query}\n"
                f"Cite the specific rule number and paraphrase the rule in your answer."
            )
        elif intent == "philosophical":
            prompt = (
                f"{system_prompt}\n\n"
                f"Here's the relevant rulebook context: {context_text}\n\n"
                f"Question: {query}\n"
                f"Explain why the rule exists in plain language, citing rule numbers if possible."
            )
        elif intent == "opinion":
            prompt = (
                f"{system_prompt}\n\n"
                f"Here's the relevant rulebook context: {context_text}\n\n"
                f"Question: {query}\n"
                f"Use teaching examples or stories from baseball to answer. If outside the rulebook, admit it but share a relevant case."
            )
        elif intent == "off_topic":
            return (
                "Hey there, that’s a bit outside the strike zone for the rulebook! "
                "Let’s stick to baseball rules or scenarios—got a question about a call or situation on the field?"
            )
        else:
            prompt = (
                f"{system_prompt}\n\n"
                f"Here's the relevant rulebook context: {context_text}\n\n"
                f"Question: {query}"
            )
        if USE_OPENAI and self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Oops, something went wrong with the rulebook lookup: {str(e)}. Try another question!"
        else:
            return f"Hey there! Based on the rulebook, here's what I found: {context_text}"
