import re
import nltk
import json
from lxml import etree

def _tokenize(text: str) -> list[str]:
    # Match alphanumeric sequences as tokens
    return re.findall(r"[a-zA-Z\d]+", text)

def _porter_stem(tokens: list[str]) -> list[str]:
    # Initialize porter stemmer
    stemmer = nltk.PorterStemmer()
    return [stemmer.stem(token.lower()) for token in tokens]

def retrieve_important(tree: etree.ElementTree) -> set[str]:
    # Retrieve the unique tokens from the bold, header, and title tags
    return set(_porter_stem(_tokenize(''.join(tree.xpath("//b|//title|//h")))))

def retrieve_content(tree: etree.ElementTree) -> list[str]:
    # Get all text content
    return _porter_stem(_tokenize(''.join(tree.xpath("//text()"))))

def _alpha_sort(indexer: dict) -> dict:
    # Sort inv. index alphabetically by token (key) in ascending order
    pairs = indexer.items() # token: document dict tuple pairs
    index_sorted = dict(sorted(pairs, key=lambda token: token[0])) # O(NlogN) for sorted() function
    return index_sorted

def partial_indexer(indexer: dict, file_count: int) -> None:
    # Write index to partial index file after 15k page threshold is met
    indexer = _alpha_sort(indexer)
    with open(f"indexed_{file_count}", "w") as f:
        json.dump(indexer, f)


