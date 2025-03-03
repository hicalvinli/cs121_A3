import json
import math
import processor
import time

STOPS = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any',
             'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below',
             'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did',
             "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few',
             'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't",
             'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself',
             'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in',
             'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most',
             "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
             'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't",
             'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than',
             'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there',
             "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those',
             'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd",
             "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's",
             'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with',
             "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours',
             'yourself', 'yourselves']

def load_doc_counts():
    with open("doc_term_counts.json", "r") as f:
        index = json.load(f)

    return index

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
def search(query, index, total_docs, doc_counts, importance_boost=0.5):

    stop_threshold = 0.5

    #Process the query
    terms = tokenize_and_stem(query)
    #Check if the query is empty
    if not terms:
        return []

    # Count number of stopwords
    stopwords = 0
    for word in terms:
        if word in STOPS:
            stopwords += 1

    stopwords = float(stopwords) / len(terms)

    #if stopwords < stop_threshold:
    #    terms = [term for term in terms if term.lower() not in STOPS]

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

            # Normalize term frequency by relative term frequency to reduce impact of execessively long files
            tf = float(tf) / doc_counts[doc] * 100

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
    doc_counts = load_doc_counts()
    index, total_docs = load_index_and_metadata()
    print(f"Index loaded with {total_docs} documents.")

    while True:
        query = input("\nEnter search query (enter '0' to quit): ").strip()
        if query == '0':
            break

        start = time.time()
        results = search(query, index, total_docs, doc_counts)
        end = time.time()
        print(f"\nTop results for '{query}':")
        #Print the top 5 URLs
        for i, (url, score) in enumerate(results[:5]):
            print(f"{i + 1}. {url} (Score: {score:.2f})")

        print(f"\nTime elapsed: {1000 * (end - start)} ms.")

if __name__ == "__main__":
    main()
