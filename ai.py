import os
from dotenv import load_dotenv # loading api key from .env for security
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API")

class Summarizer():
    def __init__(self, raw_content):
        self.site_content = raw_content

    def query(self): # sends query in form of raw text content
        client = genai.Client(api_key = GEMINI_API_KEY)

        response = client.models.generate_content(
            model = "gemini-2.0-flash",
            contents = f"Do not use text styling. Summarize this website in 2 sentences: {self.site_content}",
        )
        return response # error handling potentially?

    def summarize(self, resp): # outputs/returns model's response
        print(resp.text)

