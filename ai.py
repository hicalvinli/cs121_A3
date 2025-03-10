import os
import json
import bisect
from lxml import etree
from processor import retrieve_content
from dotenv import load_dotenv # loading api key from .env for security
from google import genai
from urllib.parse import urlparse

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API")

class Summarizer():
    # This class is designed to summarize each top search result using Google Gemini API (2.0 flash).
    def __init__(self, url):
        # Take the site's HTML info, parsed from LXML
        self.site_content = "No data."
        self.url = url
        self.response = None
        self.auth, self.first = self.extract_first()
        self.file_dirs = self.find_matching_dir()

    def extract_first(self):
        parsed_url = urlparse(self.url)
        auth = parsed_url.netloc

        return auth, auth[0]

    def query(self, keyword):
        # Sends query in form of raw text content, asking to summarize content concisely.

        # Initialize Gemini client via api key
        client = genai.Client(api_key = GEMINI_API_KEY)

        # Send response to client
        response = client.models.generate_content(
            model = "gemini-2.0-flash",
            contents = f"Do not use text styling or mention the URL name. In three factual and concise sentences, rephrase the content to emphasize its relationship to {keyword}: {self.site_content}",
        )
        # Retrieve json response
        self.response = response

    def summarize(self, resp): # outputs/returns model's response
        # Temporary for console debug. For web GUI, init Summary class and call query(), outputting response.text on click.
        # print(self.response.text)
        # WebGUI
        return self.response.text

    def find_matching_dir(self):
        # first directories that match the url based on binary search
        relative = "rsrc/DEV-2"

        dir_ls = sorted(os.listdir(relative))
        dir_ls_strip = [os.path.basename(os.path.join(os.path.abspath(relative), folder)) for folder
                        in dir_ls]

        index = bisect.bisect_left(dir_ls_strip, self.first)

        matched_dirs = []
        while index < len(dir_ls_strip) and (dir_ls_strip[index][0:1] == self.auth[0:1]):
            matched_dirs.append(dir_ls[index])
            index += 1

        return matched_dirs

    def search_corpus(self):
        # Utilizing similar processes to indexing, search corpus for corresponding link to retrieve raw, non-tokenized content.
        relative = "rsrc/DEV-2"

        # Iterate through every folder
        for folder in self.file_dirs:

            # Iterate through every file in the folder
            folder = os.path.join(os.path.abspath(relative), folder)
            basename = os.path.basename(folder)

            # further refining for www dirs
            if basename[0:2] == "www":
                if basename[4:5] != self.auth[4:5]: # check past the www. for a match
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
