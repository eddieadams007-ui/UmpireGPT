from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Test: dropped third strike rule"}]
    )
    print("Success:", response.choices[0].message.content[:100])
except Exception as e:
    print(f"Error: {e}")
