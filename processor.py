import re
import nltk
from lxml import etree

def _tokenize(text: str) -> list[str]:
    # Match alphanumeric sequences as tokens
    return re.findall(r"[a-zA-Z\d]+", text)

def _porter_stem(tokens: list[str]) -> list[str]:
    # Initialize porter stemmer
    stemmer = nltk.PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

def retrieve_important(tree: etree.ElementTree) -> set[str]:
    # Retrieve the unique tokens from the bold, header, and title tags
    return set(_porter_stem(_tokenize(''.join(tree.xpath("//b|//title|//h")))))

def retrieve_content(tree: etree.ElementTree) -> list[str]:
    # Get all text content
    return _porter_stem(_tokenize(''.join(tree.xpath("//text()"))))
