import re
import nltk
import json
import ijson
from lxml import etree

FINAL = dict()

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

def write_sub_final(bucket: list):
    global FINAL
    with open(f"index_{str(bucket[0])}-{str(bucket[-1])}", "w") as f:
        json.dump(FINAL, f)
    FINAL = dict()

def _iter_tokens(chr: str, tokens):
    global FINAL
    for token, sub_info in tokens:
        if token.startswith(chr):
            total_info = FINAL.get(token, {})
            FINAL[token] = total_info.add(sub_info)


def _split_indexes(pindex: int, bucket: tuple) -> None:
    # Splits indexes based on range.
    global FINAL
    with open(f"indexed_{pindex}", 'r') as f:
        for chr in bucket:
            # ijson turns partial index into an iterator, avoiding reading
            # it into main memory all at once.
            tokens = ijson.kvitems(f, '')
            _iter_tokens(chr, tokens)


def merge_indexes(file_num: int) -> None:
    # Merges all partial indexes alphabetically, writing each partial into a split range index
    global FINAL
    index_buckets = [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                     ('a', 'b', 'c', 'd', 'e', 'f', 'g'),
                     ('h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'),
                     ('p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')]
    for bucket in index_buckets:
        for pindex in range(1, file_num + 1):
            _split_indexes(file_num, bucket)
            FINAL = _alpha_sort(FINAL)
