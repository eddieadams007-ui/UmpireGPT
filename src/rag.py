import os
import json
import re
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
            return "rule_reference"
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a baseball coach classifying user questions into one of these intents: 'scenario_based' (describes a game situation with outs, runners, or umpire calls, e.g., 'two outs, runner on first, dropped third strike'), 'rule_reference' (asks for a specific rule definition, e.g., 'What is the infield fly rule?'), 'philosophical' (asks why a rule exists, e.g., 'Why do we have the infield fly rule?'), 'opinion' (asks for stories or opinions), 'off_topic' (unrelated to baseball rules). Respond with only the intent name."},
                    {"role": "user", "content": query}
                ]
            )
            intent = response.choices[0].message.content.strip()
            # Fallback check for scenario_based
            query_lower = query.lower()
            if any(keyword in query_lower for keyword in ['out ', 'outs ', 'no outs', 'one out', 'two outs', 'runner', 'runners', 'on first', 'on second', 'on third', 'bases loaded', 'call ', 'umpire', 'correct', 'right', 'wrong', 'called']):
                intent = "scenario_based"
            return intent
        except Exception:
            return "rule_reference"

    def check_scenario_slots(self, query):
        """Check if scenario-based question has required slots (outs, runners, call_made)."""
        required_slots = ["outs", "runners", "call_made"]
        present_slots = []
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in ['out ', 'outs ', 'no outs', 'one out', 'two outs']):
            present_slots.append('outs')
        if any(keyword in query_lower for keyword in ['runner', 'runners', 'on first', 'on second', 'on third', 'bases loaded', 'base']):
            present_slots.append('runners')
        if any(keyword in query_lower for keyword in ['call ', 'umpire', 'correct', 'right', 'wrong', 'called']):
            present_slots.append('call_made')
        missing_slots = [slot for slot in required_slots if slot not in present_slots]
        return missing_slots

    def standardize_rule_id(self, doc_id, doc, idmap):
        """Standardize rule ID from idmap and doc (e.g., '2.00' and 'Balk' to 'Rule 2.00 (Balk)')."""
        idx = list(idmap.index).index(int(doc_id.split('_')[-1]) if 'doc_' in doc_id else int(doc_id))
        rule = idmap.iloc[idx].get('rule', '')
        rule_sub = idmap.iloc[idx].get('rule_sub', '')
        rule_sub = rule_sub.lstrip('0') if rule_sub.startswith('0.') else rule_sub
        rule_id = f"{rule}{rule_sub}" if rule_sub else rule
        term = doc.get('define', doc.get('c_verbatim', '')).strip()
        if not term:
            term_match = re.search(r'– ([^\.:]+)', doc.get('text', ''))
            term = term_match.group(1).strip() if term_match else ''
        return f"Rule {rule_id} ({term})" if term else f"Rule {rule_id}"

    def generate_answer(self, query, context, idmap):
        if not context:
            return "Hey there! I couldn't find any relevant rules in the rulebook for that one. Can you clarify or ask something else?", 0
        if not os.path.exists(self.data_path) or not os.path.exists(self.index_path):
            return "Oops, something went wrong—couldn't find the rulebook data. Let's try another question!", 0
        
        context_with_ids = []
        for doc in context:
            doc_id = idmap.get(list(idmap.index).index(int(doc['id'].split('_')[-1]) if 'doc_' in doc['id'] else int(doc['id'])), doc['id'])
            standardized_id = self.standardize_rule_id(doc_id, doc, idmap)
            context_with_ids.append(f"{standardized_id}: {doc['text']}")
        context_text = " ".join(context_with_ids)
        
        intent = self.classify_intent(query)
        if intent == "scenario_based":
            missing_slots = self.check_scenario_slots(query)
            if missing_slots:
                return f"Hey coach, I need a bit more info to nail this call! Can you tell me about {', '.join(missing_slots)}? For example, how many outs are there, and who's on base?", 0
        
        system_prompt = (
            "You are UmpGPT, an authoritative but approachable instructor and umpire for Little League Baseball International (LLI). "
            "Your mission is to give the correct ruling and a brief, clear explanation that a manager can act on immediately. "
            "Always cite exact sources from the Official Little League Rulebook (e.g., Rule 7.13 NOTE or Rule 6.09(b)). "
            "NEVER invent a rule or section number. If a rule number is unavailable, cite the section title (e.g., Interference—LL Rulebook). "
            "Assume Baseball unless Softball is specified. Match the user’s division (Tee Ball, Minors, Majors, etc.) if provided, or default to Majors/Minors. "
            "Use a professional, confident, and supportive tone, like a trusted umpire at a plate meeting. "
            "Structure your response with: **Ruling**: One-sentence call (e.g., safe/out). **Why**: Short, plain-English explanation. **Rule References**: Exact rule/section identifiers. **Key Conditions Recap**: Bullet points listing critical conditions. **Live/Dead Ball**: Status of the ball. **Example**: Practical scenarios. **Division Note**: Clarify if rules differ by division (e.g., Minors vs. Majors). "
            "For philosophical questions, explain the rule’s purpose with citations. For opinion questions, use teaching examples or admit if outside the rulebook. For off-topic questions, redirect to baseball rules. "
            "For scenario-based queries, ensure rulings are precise, especially for dropped third strike scenarios (Rule 6.09(b)): with two outs, the batter is not automatically out and can attempt to reach first base if the catcher drops the third strike, regardless of runners on base."
        )
        
        if intent == "rule_reference":
            prompt = (
                f"{system_prompt}\n\n"
                f"Here's the relevant rulebook context: {context_text}\n\n"
                f"Question: {query}\n"
                f"Provide a structured response with: **Ruling**: One-sentence definition or call. **Why**: Brief explanation of the rule. **Rule References**: Exact rule numbers (e.g., Rule 2.00, 6.05(d)). **Key Conditions Recap**: Bullet points listing conditions. **Live/Dead Ball**: Status of the ball. **Example**: Practical scenario. **Division Note**: Clarify division-specific rules if applicable."
            )
        elif intent == "philosophical":
            prompt = (
                f"{system_prompt}\n\n"
                f"Here's the relevant rulebook context: {context_text}\n\n"
                f"Question: {query}\n"
                f"Explain the rule’s purpose in plain language with exact rule citations, using the structure: **Ruling**: One-sentence summary. **Why**: Purpose explanation. **Rule References**: Exact citations (e.g., Rule 2.00, 6.05(d)). **Key Conditions Recap**: Bullet points listing conditions. **Live/Dead Ball**: Status of the ball. **Example**: Practical scenario. **Division Note**: Clarify division-specific rules if applicable."
            )
        elif intent == "opinion":
            prompt = (
                f"{system_prompt}\n\n"
                f"Here's the relevant rulebook context: {context_text}\n\n"
                f"Question: {query}\n"
                f"Use teaching examples or stories, admitting if outside the rulebook, with the structure: **Ruling**: One-sentence response. **Why**: Explanation or story. **Rule References**: Cite rules if applicable. **Key Conditions Recap**: Bullet points if relevant. **Live/Dead Ball**: Status if relevant. **Example**: Practical scenario. **Division Note**: Clarify if relevant."
            )
        elif intent == "off_topic":
            return (
                "Hey there, that’s a bit outside the strike zone for the rulebook! "
                "Let’s stick to baseball rules or scenarios—got a question about a call or situation on the field?", 0
            )
        else:
            prompt = (
                f"{system_prompt}\n\n"
                f"Here's the relevant rulebook context: {context_text}\n\n"
                f"Question: {query}\n"
                f"Provide a structured response with: **Ruling**: One-sentence call. **Why**: Brief explanation. **Rule References**: Exact rule numbers (e.g., Rule 2.00, 6.05(d)). **Key Conditions Recap**: Bullet points listing conditions. **Live/Dead Ball**: Status of the ball. **Example**: Practical scenarios. **Division Note**: Clarify division-specific rules if applicable."
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
                answer = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if response.usage else 0
                return answer, tokens_used
            except Exception as e:
                return f"Oops, something went wrong with the rulebook lookup: {str(e)}. Try another question!", 0
        else:
            return f"Hey there! Based on the rulebook, here's what I found: {context_text}", 0
