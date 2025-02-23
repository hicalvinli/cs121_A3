import json
from collections import namedtuple
import os

from lxml import etree

from processor import retrieve_important, retrieve_content

# Inverted INDEX data structure will be a
# dictionary: key: token -> value: dictionary of documents where key: documentname -> value: namedtuple
# named tuple will contain (wordfrequency, importance)

THRESHOLD = 15000 # for every 15k pages, partially INDEX into disk memory (new file, INDEXed_{num})
FILE_COUNT = 1 # count for number of partial INDEXes
INDEX = dict()
Docinfo = namedtuple('Docinfo', ['wordfrequency', 'importance'])
def updateIndex(word, importance):
    # if the word doesnt exist add it and give it a dictionary add the document
    if INDEX.get(word) is None:
        INDEX[word] = dict()
        INDEX[word][jsondata['url']] = Docinfo(1, importance)
    # if the word exists check if your current doc has already been added
    else:
        # so only update word frequency
        if INDEX[word].get(jsondata['url']) is not None:
            INDEX[word][jsondata['url']]._replace(wordfrequency=INDEX[word][jsondata['url'] + 1])
        # if document doesn't exist, add it to the dictionary
        else:
            INDEX[word][jsondata['url']] = Docinfo(1, importance)


# 1) Loop through the JSON files and load them and get their content
def main():
    file_count = 0
    for files in os.listdir("rsrc/DEV-2"):
        file_count += 1
        with open(files, "r") as file:
            jsondata = json.load(file)
        try:
            tree = etree.fromstring(jsondata['content'], etree.HTMLParser())
            # 2) retrieve important
            important_list = retrieve_important(tree)
            # 3) retrieve content
            regular_list = retrieve_content(tree)
            # 4) populate the INDEX
            # 5a) create a var. to count number of files scraped, or loop until threshold is met. call partial
            # INDEXer after.
            # 5b) set counter variable back to 0 for next batch of 15k files
            for word in important_list:
                updateIndex(word, 1)
            for word in regular_list:
                updateIndex(word, 0)
        except Exception as e:
            print("failed tree")

    with open("data.json", "w") as file:
        json.dump(INDEX, file)

    print("DUMPED")

