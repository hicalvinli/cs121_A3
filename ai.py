import os
from dotenv import load_dotenv # loading api key from .env for security
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API")

class Summarizer():
    def __init__(self, raw_content):
        self.site_content = raw_content

    def query(self): # sends query in form of raw text content
        pass

    def summarize(self, resp): # outputs/returns model's response
        pass

