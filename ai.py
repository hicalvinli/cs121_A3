import os
import json

from lxml import etree
from processor import retrieve_content
from dotenv import load_dotenv # loading api key from .env for security
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API")

class Summarizer():
    # This class is designed to summarize each top search result using Google Gemini API (2.0 flash).
    def __init__(self, url):
        # Take the site's HTML info, parsed from LXML
        self.site_content = "No data."
        self.url = url
        self.response = None

    def query(self, keyword):
        # Sends query in form of raw text content, asking to summarize content concisely.

        # Initialize Gemini client via api key
        client = genai.Client(api_key = GEMINI_API_KEY)

        # Send response to client
        response = client.models.generate_content(
            model = "gemini-2.0-flash",
            contents = f"Do not use text styling. In three sentences, rephrase the content to emphasize its relationship to {keyword}: {self.site_content}",
        )
        # Retrieve json response
        self.response = response

    def summarize(self, resp): # outputs/returns model's response
        # Temporary for console debug. For web GUI, init Summary class and call query(), outputting response.text on click.
        print(self.response.text)

    def search_corpus(self):
        # Utilizing similar processes to indexing, search corpus for corresponding link to retrieve raw, non-tokenized content.
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

                    # Check if URL from file matches search result URL
                    if str(self.url) == str(json_data["url"]):
                        tree = etree.fromstring(bytes(json_data['content'], encoding = 'utf-8'),
                                                etree.HTMLParser())

                        # grab entire content
                        full_content, non_stem, regular_list = retrieve_content(tree)

                        self.site_content = full_content
