import json
import math
import processor
import time


SPLITS = [('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'),
                 ('a', 'b', 'c', 'd', 'e', 'f', 'g'),
                 ('h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'),
                 ('p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')]

def load_index_and_metadata(term):
    global SPLITS
    #Load the inverted index based on its alphanumeric file split
    if term[0] in SPLITS[0]:
        file_name = '0-9.json'
    elif term[0] in SPLITS[1]:
        file_name = 'a-g.json'
    elif term[0] in SPLITS[2]:
        file_name = 'h-o.json'
    else:
        file_name = 'p-z.json'

    with open(file_name, "r") as f:
        #Read the json data from the file
        #Convert the data into a Python dict, this is the inverted index
        index = json.load(f)

    all_urls = set()
    #Iterate over each term in the index
    for term in index:
        #Add the keys to the set for each term
        all_urls.update(index[term].keys())
    #Count the number of unique documents
    total_docs = len(all_urls)

    #Return the inverted index and total number of unique documents
    return index, total_docs

#Basically the same thing we did before lmao
def tokenize_and_stem(query):
    #Tokenize and stem
    return processor._porter_stem(processor._tokenize(query))

#Search function
def search(query, importance_boost=0.5):
    index = {}
    total_docs = 0
    #Process the query
    terms = tokenize_and_stem(query)
    #Check if the query is empty
    if not terms:
        return []

    #Check if terms exist in the index
    #Iterate over each stemmed term
    for term in terms:
        #Check if the term is present in the inverted index
        index, total_docs = load_index_and_metadata(term)

        print(f"Index loaded with {total_docs} documents.")
        if term not in index:
            #Return empty if any term is not found in the index
            #There are no documents containing all the terms
            return []

    #Get document lists for each term
    doc_sets = [set(index[term].keys()) for term in terms]

    #Get intersection
    #Initalize common_docs with the set of documents for the first term
    common_docs = doc_sets[0]
    #Iterate over remaining sets
    for doc_set in doc_sets[1:]:
        #Update common_docs with the intersection of each subsequent set
        common_docs.intersection_update(doc_set)
        #Check if the intersection is empty
        if not common_docs:
            #Return empty if non common documents exist
            return []

    #Calculate importance scores for each document
    scores = []
    #Loop through each document that contains all query terms
    for doc in common_docs:
        score = 0.0
        #Iterate over each term in the query
        for term in terms:
            #Retrieve term frequency (tf) and associate importance value for the termin in the document from the index
            tf, importance = index[term][doc]
            #Compute document frequency (df)
            df = len(index[term])
            #Calculate inverse document frequency
            #IDF = log(total number of documents in corpus D/number of documents containing term t)
            idf = math.log(total_docs / df) if df else 0 #return 0 if document frequency is 0
            term_score = tf * idf * (1 - importance_boost * importance)
            #Add the term's score to the document score
            score += term_score
        #Append scores
        scores.append((doc, score))

    #Return list in descending order
    return sorted(scores, key=lambda x: -x[1])

def main():
    # index, total_docs = load_index_and_metadata()

    while True:
        query = input("\nEnter search query (enter '0' to quit): ").strip()
        if query == '0':
            break

        start = time.time()
        results = search(query)
        end = time.time()
        print(f"\nTop results for '{query}':")
        #Print the top 5 URLs
        for i, (url, score) in enumerate(results[:5]):
            print(f"{i + 1}. {url} (Score: {score:.2f})")

        print(f"\nTime elapsed: {1000 * (end - start)} ms.")

if __name__ == "__main__":
    main()
