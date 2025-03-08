import os
from dotenv import load_dotenv # loading api key from .env for security
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API")

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Are you excited to be a website summarizer?",
)

print(response.text)