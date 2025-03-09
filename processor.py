import re
import nltk
import json
import ijson
import hashlib
import tokenizer
from lxml import etree

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

    # Get all text content, returns non tokenized, non stemmed, and stemmed
    return ' '.join(tree.xpath("//text()")), _tokenize(' '.join(tree.xpath("//text()"))), _porter_stem(_tokenize(' '.join(tree.xpath("//text()"))))

def _alpha_sort(indexer: dict) -> dict:
    # Sort inv. index alphabetically by token (key) in ascending order
    pairs = indexer.items() # token: document dict tuple pairs
    index_sorted = dict(sorted(pairs, key=lambda token: token[0])) # O(NlogN) for sorted() function
    return index_sorted

def partial_indexer(indexer: dict, pfile_count: int) -> None:
    # Write index to partial index file after 15k page threshold is met
    indexer = _alpha_sort(indexer)
    with open(f"indexed_{pfile_count}.json", "w") as f:

        for key in indexer:
            f.write(f"{key}: {str(indexer[key])[1:-1]}\n")

def index_min(ls: list) -> int:
    if len(ls) == 0:
        return -1

    min = 0
    for i in range(1, len(ls)):
        if ls[i] < ls[min]:
            min = i
    return min

def merge_indexes(file_num: int) -> None:
    # Merges all partial indexes alphabetically, writing each partial into a file

    global SECONDARY_INDEX
    byte_count = 0
    open_fds = file_num

    with open("data.json", "w") as merged:
        # Open all files and append first line into terms list
        fds = list()
        terms = list()
        for i in range(1, file_num + 1):
            fds.append(open(f"indexed_{i}.json", "r"))
            terms.append(fds[i - 1].readline())

            if terms[i - 1] == "":
                fds[i - 1].close()
                open_fds -= 1
                terms[i - 1] = "\uffff"
            else:
                # Process each term line
                terms[i - 1] = terms[i - 1].split(": ", 1)

        # Initialize vars
        smallest_index = index_min([t[0] for t in terms])
        smallest = terms[smallest_index]
        terms[smallest_index] = fds[smallest_index].readline()
        if terms[smallest_index] == "":
            terms[smallest_index] = ["\uffff"]

        # While there is still an open file
        while not all(fd.closed for fd in fds):

            # Get lexicographically smallest term
            next_smallest_index = index_min([t[0] for t in terms])
            next_smallest = terms[next_smallest_index]

            # If next smallest is equivalent keys, merge the values
            if next_smallest[0] == smallest[0]:
                smallest[1] = smallest[1] + " " + next_smallest[1]
            else:
                to_write = f"{smallest[0]}: {smallest[1]}"
                merged.write(to_write)
                SECONDARY_INDEX[smallest[0]] = byte_count
                byte_count += len(to_write)
                smallest = next_smallest

            # Read next
            terms[next_smallest_index] = fds[next_smallest_index].readline().split(": ", 1)

            # If next is empty, close
            if "" in terms[next_smallest_index]:
                fds[next_smallest_index].close()
                open_fds -= 1
                terms[next_smallest_index] = ["\uffff"]

                # If there is only one fd open left, iterate to write all of those and exit
                if open_fds == 1:

                    # Find open
                    smallest_index = 0
                    for i in range(len(fds)):
                        if not fds[i].closed:
                            smallest_index = i
                            break

                    # Write all remaining
                    while smallest[0] != "":
                        to_write = f"{smallest[0]}: {smallest[1]}"
                        merged.write(to_write)
                        SECONDARY_INDEX[smallest[0]] = byte_count
                        byte_count += len(to_write)
                        smallest = fds[smallest_index].readline().split(": ", 1)

                    # Close and dump second
                    fds[smallest_index].close()
                    with open("secondary_index.json", "w") as f:
                        json.dump(SECONDARY_INDEX, f)

                    # Exit
                    return

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