import json
from collections import namedtuple
import os
import time
import processor
from lxml import etree

from processor import retrieve_important, retrieve_content
import time

# Inverted INDEX data structure will be a
# dictionary: key: token -> value: dictionary of documents where key: documentname -> value: namedtuple
# named tuple will contain (wordfrequency, importance)

THRESHOLD = 15000 # for every 15k pages, partially index into disk memory (new file, indexed_{num})
FILE_COUNT = 0 # checking if threshold matches number of files
PFILE_COUNT = 0 # count for number of partial indexes
INDEX = dict()
DOC_COUNTS = dict()
Docinfo = namedtuple('Docinfo', ['wordfrequency', 'importance'])
HASHES = dict() # for checking document duplicates
SIMHASHES = dict() # for checking near duplicates

def updateIndex(word, url):
    global INDEX
    # if the word doesn't exist add it and give it a dictionary add the document
    if not INDEX.get(word, False):
        INDEX[word] = dict()
        INDEX[word][url] = Docinfo(1, 0)

    # if the word exists check if your current doc has already been added
    else:
        # so only update word frequency
        if INDEX[word].get(url, False):
            INDEX[word][url] = Docinfo(INDEX[word][url].wordfrequency + 1, 0)

        # if document doesn't exist, add it to the dictionary
        else:
            INDEX[word][url] = Docinfo(1, 0)


# 1) Loop through the JSON files and load them and get their content
# 1.5) need to check sum and simhash
def main():
    global THRESHOLD
    global FILE_COUNT
    global PFILE_COUNT
    global DOC_COUNTS
    global INDEX
    relative = "rsrc/DEV-2"

    # Iterate through every folder
    for folder in os.listdir(relative):
        print(FILE_COUNT)

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
                jsondata = json.load(f)

            try:
                # Parse the html, enforcing coding to align with fromstring() requirements
                tree = etree.fromstring(bytes(jsondata['content'], encoding='utf-8'), etree.HTMLParser())

                if tree is None:
                    continue

                # 2 & 3) Tokenize important content and all content
                full_content, non_stem, regular_list = retrieve_content(tree)
                important_set = retrieve_important(tree)

                non_stem = ' '.join(non_stem)

                # avoiding duplicates or near duplicates and low to no content files
                if len(regular_list) > 75 and processor.is_duplicate(non_stem, HASHES, SIMHASHES) is False:
                    # Increment file count
                    FILE_COUNT += 1
                    # 4) populate the index
                    url = jsondata['url']

                    # Save the total term count
                    DOC_COUNTS[url] = len(regular_list)

                    # For every word update the index with it
                    for word in regular_list:
                        updateIndex(word, url)

                    # For every important word, update its importance
                    for word in important_set:
                        INDEX[word][url] = INDEX[word][url]._replace(importance=1)

                    # 5a) Loop until threshold is met with file_count. call partial indexer after.
                    if THRESHOLD <= FILE_COUNT:
                        PFILE_COUNT += 1
                        processor.partial_indexer(INDEX, PFILE_COUNT)
                        # 5b) set counter variable back to 0 for next batch of 15k files
                        FILE_COUNT = 0
                        INDEX = dict()
                        print(f"partial index {PFILE_COUNT} dumped")
                # else:
                #     print('\nDUPLICATE DETECTED')
                #     print(non_stem, "\n")
                # print("\n")
                # time.sleep(5)

            except Exception as e:
                print(f"failed: {e} at line:", e.__traceback__.tb_lineno)

    # last few files
    PFILE_COUNT += 1
    processor.partial_indexer(INDEX, PFILE_COUNT)

    # set counter variable back to 0 for next batch of 15k files
    FILE_COUNT = 0
    INDEX = dict()
    print(f"partial index {PFILE_COUNT} dumped")

    # merge
    processor.merge_indexes(PFILE_COUNT)
    print("Secondary index dumped")

    # Write document term count file
    with open("doc_term_counts.json", "w") as f:
        json.dump(DOC_COUNTS, f)
    print("Dumped document term counts.")

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Time elapsed:", end - start, "seconds")