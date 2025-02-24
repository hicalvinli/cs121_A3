import re
import nltk
import json
import ijson
import hashlib
import tokenizer
from lxml import etree

FINAL = dict()

def _tokenize(text: str) -> list[str]:
    # Match alphanumeric sequences as tokens
    return re.findall(r"[a-zA-Z\d]+", text.lower())

def _porter_stem(tokens: list[str]) -> list[str]:
    # Initialize porter stemmer
    stemmer = nltk.PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

def retrieve_important(tree: etree.ElementTree) -> set[str]:
    # Retrieve the unique tokens from the bold, header, and title tags
    tags = tree.xpath("//b|//title|//h")
    content = ""

    # For each retrieved tag, add content to content
    for tag in tags:
        content += ' ' +  ' '.join(tag.itertext())

    # Return set of stemmed tokens
    return set(_porter_stem(_tokenize(content)))

def retrieve_content(tree: etree.ElementTree) -> list[str]:
    # Remove all JS and css script/style tags
    to_drop = tree.xpath('//style|//script')
    for tag in to_drop:
        tag.getparent().remove(tag)

    # Get all text content
    return _porter_stem(_tokenize(' '.join(tree.xpath("//text()"))))

def _alpha_sort(indexer: dict) -> dict:
    # Sort inv. index alphabetically by token (key) in ascending order
    pairs = indexer.items() # token: document dict tuple pairs
    index_sorted = dict(sorted(pairs, key=lambda token: token[0])) # O(NlogN) for sorted() function
    return index_sorted

def partial_indexer(indexer: dict, pfile_count: int) -> None:
    # Write index to partial index file after 15k page threshold is met
    indexer = _alpha_sort(indexer)
    with open(f"indexed_{pfile_count}", "w") as f:
        json.dump(indexer, f)

def _write_sub_final(bucket: tuple):
    # Writes the final index of each bucket into its corresponding file.
    global FINAL
    with open(f"{str(bucket[0])}-{str(bucket[-1])}", "w") as f: # new file with bucket range
        json.dump(FINAL, f)
    FINAL = dict()

def _split_indexes(pindex: int, bucket: tuple) -> None:
    # Splits indexes based on range.
    global FINAL
    with open(f"indexed_{pindex}", 'r') as f:
        # ijson turns partial index into an iterator, avoiding reading
        # it into main memory all at once.
        for token, sub_info in ijson.kvitems(f, ''):
            if token[0] in bucket:
                total_info = FINAL.get(token, {}) # check if token already exists in the final index
                total_info.update(sub_info) # add additional document info to the token
                FINAL[token] = total_info # update the final index with the additional information

def merge_indexes(file_num: int) -> None:
    # Merges all partial indexes alphabetically, writing each partial into a split range index
    global FINAL
    index_buckets = [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                     ('a', 'b', 'c', 'd', 'e', 'f', 'g'),
                     ('h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'),
                     ('p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')]
    for bucket in index_buckets:
        for pindex in range(1, file_num + 1):
            _split_indexes(pindex, bucket)
        FINAL = _alpha_sort(FINAL)
        _write_sub_final(bucket)

def checksum(content: str) -> bool:
    # Calculate checksum for a string and return. Utilizing hashlib MD5 for medium strength
    # and speed hashing. Checks existence of hash within dictionary. Returns True if duplicate,
    # else False.
    global HASHES
    md5_hash = hashlib.md5(content.encode()).hexdigest()
    result = HASHES.get(md5_hash, False)
    HASHES[md5_hash] = True
    return result


def simhash(content: str) -> bool:
    # Calculate simhash and return TRUE if is a near duplicate and FALSE if a new document that isn't
    # 1) Tokenize the input document into "features" which are words in our case, and assign weight using word frequency
    tokenlist = tokenizer.tokenize(content)
    wordfreq = dict()
    tokenizer.computeWordFrequencies(tokenlist, wordfreq)

    # 2) Hash each feature using MD5 (128 bit)  For each feature, convert its hash to a binary number,
    hash_dict = dict()
    for word in wordfreq.keys():
        md5_hash = hashlib.md5(word.encode()).digest()
        # .join needs a iterable, thats why for loop is inside, '08b' means turn each raw byte in 8 bit string
        md5_binary_str = ''.join(format(byte, '08b') for byte in md5_hash)
        hash_dict[md5_binary_str] = wordfreq[word]

    # 3) Create a vector of 0s that are the same length as the hash length
    # digest makes 16 bytes 8 bits each
    sum_vec = [0] * 128

    # 4) for each bit in each features binary str, if a bit is 1, add the weight to the corresponding slot
    # in the vector, if it is 0, then subtract the features weight from that slot
    for word in hash_dict:
        for i in range(0,128):
            if word[i] == '1':
                sum_vec[i] += hash_dict[word]
            else:
                sum_vec[i] -= hash_dict[word]

    # 5) After going through each feature, if a slot's sum is positive, it becomes 1, if negative, 0
    binary_string = ""
    for i in sum_vec:
        if i > 0:
            binary_string += "1"
        else:
            binary_string += "0"
    simhash_value = int(binary_string, 2)

    global SIMHASHES
    # 6) Compare documents using fraction of bits that are similar
    for sim in SIMHASHES:
        different_bits = bin(simhash_value ^ sim).count("1") # XOR operation to see which bits are different
        same_bits = 128 - different_bits
        if (same_bits/128) > .9:
            return True
    SIMHASHES[simhash_value] = True
    return False