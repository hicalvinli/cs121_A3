import json
import math
import processor
import time

def load_index_and_metadata():
    #Load the inverted index
    with open("data.json", "r") as f:
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
def search(query, index, total_docs, importance_boost=0.5):
    #Process the query
    terms = tokenize_and_stem(query)
    #Check if the query is empty
    if not terms:
        return []

    #Check if terms exist in the index
    #Iterate over each stemmed term
    for term in terms:
        #Check if the term is present in the inverted index
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
    index, total_docs = load_index_and_metadata()
    print(f"Index loaded with {total_docs} documents.")

    while True:
        query = input("\nEnter search query (enter '0' to quit): ").strip()
        if query == '0':
            break

        start = time.time()
        results = search(query, index, total_docs)
        end = time.time()
        print(f"\nTop results for '{query}':")
        #Print the top 5 URLs
        for i, (url, score) in enumerate(results[:5]):
            print(f"{i + 1}. {url} (Score: {score:.2f})")

        print(f"\nTime elapsed: {1000 * (end - start)} ms.")

if __name__ == "__main__":
    main()
