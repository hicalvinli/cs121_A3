import re
import nltk
import json
import ijson
import hashlib
import tokenizer
from lxml import etree

FINAL = dict()
SECONDARY_INDEX = dict()

def _tokenize(text: str) -> list[str]:
    # Match alphanumeric sequences as tokens
    return re.findall(r"[a-zA-Z\d]+", text.lower())

def _porter_stem(tokens: list[str]) -> list[str]:
    # Initialize porter stemmer
    stemmer = nltk.PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

def retrieve_important(tree: etree.ElementTree) -> set[str]:
    # Retrieve the unique tokens from the bold, header, strong, and title tags
    tags = tree.xpath("//b|//title|//h|//strong")
    content = ""

    # For each retrieved tag, add content to content
    for tag in tags:
        content += ' ' +  ' '.join(tag.itertext())

    # Return set of stemmed tokens
    return set(_porter_stem(_tokenize(content)))

def retrieve_content(tree: etree.ElementTree) -> tuple:
    # Remove all JS and css script/style tags
    to_drop = tree.xpath('//style|//script')
    for tag in to_drop:
        tag.getparent().remove(tag)

    # Get all text content, returns non stemmed and stemmed
    return _tokenize(' '.join(tree.xpath("//text()"))), _porter_stem(_tokenize(' '.join(tree.xpath("//text()"))))

def _alpha_sort(indexer: dict) -> dict:
    # Sort inv. index alphabetically by token (key) in ascending order
    pairs = indexer.items() # token: document dict tuple pairs
    index_sorted = dict(sorted(pairs, key=lambda token: token[0])) # O(NlogN) for sorted() function
    return index_sorted

def partial_indexer(indexer: dict, pfile_count: int) -> None:
    # Write index to partial index file after 15k page threshold is met
    indexer = _alpha_sort(indexer)
    with open(f"indexed_{pfile_count}.json", "w") as f:
        json.dump(indexer, f)

def _write_sub_final(bucket: tuple):
    # Writes the final index of each bucket into its corresponding file.
    global FINAL
    with open(f"{str(bucket[0])}-{str(bucket[-1])}.json", "w") as f: # new file with bucket range
        json.dump(FINAL, f)
    FINAL = dict()

def write_full():
    all_ind = ["0-9.json", "a-g.json", "h-o.json", "p-z.json"]
    comb = {}
    with open("data.json", "w") as f:
        byte_count = 0
        for pind in all_ind:
            with open(pind, "r") as f2:
                comb = (json.load(f2))
    # when you get the big data file, calculate the byte offset and place them into the secondary index
    # term with start with " and end with ", then keep adding until you see } <- this will indicate end of
    # documents for that term, then count until next ", and repeat :D
    # instead of dumping i will manually write to the dict on my own so i can count the bytes while writing
                comb_len = len(comb)
                i = 0
                for key, value in comb.items():
                    # this will assign byte_count for the term, then write the key value in json format
                    SECONDARY_INDEX[key] = byte_count
                    if i >= comb_len - 1 and pind == "p-z.json":
                        pair_str = '"' + str(key) + '"' + ": " + str(value) + "}"
                    else:
                        pair_str = '"' + str(key) + '"' + ": " + str(value) + ", "
                    # last key is special
                    f.write(pair_str)
                    byte_count += len(pair_str)
                    # add 2 bc 1 comma, and 1 space, and {}
                    i += 1

    with open("secondary_index.json", "w") as f:
        json.dump(SECONDARY_INDEX, f)

    print(SECONDARY_INDEX)
    # with open("data.json", "w") as f:
        # json.dump(comb, f)

def _split_indexes(pindex: int, bucket: tuple) -> None:
    # Splits indexes based on range.
    global FINAL
    with open(f"indexed_{pindex}.json", 'r') as f:
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
    index_buckets = [('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'),
                     ('a', 'b', 'c', 'd', 'e', 'f', 'g'),
                     ('h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'),
                     ('p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')]
    for bucket in index_buckets:
        for pindex in range(1, file_num + 1):
            _split_indexes(pindex, bucket)
        FINAL = _alpha_sort(FINAL)
        _write_sub_final(bucket)

def is_duplicate(content, HASHES, SIMHASHES):
    return _checksum(content, HASHES) or _simhash(content, SIMHASHES)

def _checksum(content: str, HASHES: dict) -> bool:
    # Calculate checksum for a string and return. Utilizing hashlib MD5 for medium strength
    # and speed hashing. Checks existence of hash within dictionary. Returns True if duplicate,
    # else False.
    md5_hash = hashlib.md5(content.encode()).hexdigest()
    if md5_hash in HASHES:
        return True
    HASHES[md5_hash] = True
    return False


def _simhash(content: str, SIMHASHES: dict) -> bool:
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

    # 6) Compare documents using fraction of bits that are similar
    for sim in SIMHASHES:
        different_bits = bin(simhash_value ^ sim).count("1") # XOR operation to see which bits are different
        same_bits = 128 - different_bits
        if (same_bits/128) > .9:
            return True
    SIMHASHES[simhash_value] = True
    return False