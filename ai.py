import os
import json

from lxml import etree
from processor import retrieve_content
from dotenv import load_dotenv # loading api key from .env for security
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API")

class Summarizer():
    def __init__(self, raw_content):
        self.site_content = raw_content

    def query(self, keyword): # sends query in form of raw text content
        client = genai.Client(api_key = GEMINI_API_KEY)

        response = client.models.generate_content(
            model = "gemini-2.0-flash",
            contents = f"Do not use text styling. In three sentences, rephrase the content to emphasize its relationship to {keyword}: {self.site_content}",
        )
        return response # error handling potentially?

    def summarize(self, resp): # outputs/returns model's response
        print(resp.text)


def search_corpus(url):
    relative = "rsrc/DEV-2"

    # Iterate through every folder
    for folder in os.listdir(relative):

        # Iterate through every file in the folder
        folder = os.path.join(os.path.abspath(relative), folder)

        # Skip hidden folders/files
        if os.path.basename(folder).startswith("."):
            continue

        for file in os.listdir(folder):
            # Skip hidden folders/files
            if os.path.basename(file).startswith("."):
                continue

            # Open file and load json
            file = os.path.join(folder, file)
            with open(file, "r") as f:
                json_data = json.load(f)
                if str(url) == str(json_data["url"]):
                    tree = etree.fromstring(bytes(json_data['content'], encoding = 'utf-8'),
                                            etree.HTMLParser())

                    # grab entire content
                    full_content, non_stem, regular_list = retrieve_content(tree)

                    return full_content
    return "data not found"