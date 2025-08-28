from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    resp = client.embeddings.create(
        model="text-embedding-3-large",
        input="Hello world"
    )
    print("Embedding generated! Length:", len(resp.data[0].embedding))
except Exception as e:
    print("Error:", e)