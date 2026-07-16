import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("KIMCHI_API_KEY", "castai_v1_aa7f06d5b11127958cd3d26ad4a2ac6ce4c75e11207d1005db4b891191b51675_c627222c"),
    base_url="https://llm.kimchi.dev/openai/v1"
)

try:
    response = client.chat.completions.create(
        model="kimi-k2.7",
        messages=[{"role": "user", "content": "What is 2+2?"}]
    )
    print("Success:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
