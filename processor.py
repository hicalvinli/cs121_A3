import re
import nltk
from lxml import etree

def tokenize(text):
    # Match alphanumeric sequences as tokens
    return re.findall(r"[a-zA-Z\d]+", text)

def porter_stem(tokens):
    # Initialize porter stemmer
    stemmer = nltk.PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

def retrieve_important(tree: etree.ElementTree):
    # Retrieve the unique tokens from the bold, header, and title tags
    return set(tokenize(''.join(tree.xpath("//b|//title|//h"))))

def retrieve_content(tree: etree.ElementTree):
    # Get all text content
    return tokenize(''.join(tree.xpath("//text()")))
