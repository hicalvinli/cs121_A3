from collections import namedtuple

# Inverted index data structure will be a
# dictionary: key: token -> value: dictionary of documents where key: documentname -> value: namedtuple
# named tuple will contain (wordfrequency, importance)

THRESHOLD = 15000 # for every 15k pages, partially index into disk memory (new file, indexed_{num})
FILE_COUNT = 0 # count for number of partial indexes

Docinfo = namedtuple('Docinfo', ['wordfrequency', 'importance'])

index = dict()

# 1) Loop through all the JSON files and load them and get their content

# 2) tokenize the content

# 3) retrieve content

# 4) retrieve important

# 5) populate the index