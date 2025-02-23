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
    # Retrieve the content from the bold, header, and title tags
    return ''.join(tree.xpath("//b|//title|//h"))

def retrieve_content(tree: etree.ElementTree):
    # Remove the bold, header, and title tags
    to_drop = tree.xpath('//b|//title|//h')
    for tag in to_drop:
        tag.getparent().remove(tag)

    # Get all text content
    return ''.join(tree.xpath("//text()"))