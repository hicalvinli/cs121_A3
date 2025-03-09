import json
import math
import re

import processor
import ai
import time

SECONDARY_INDEX = dict()
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

def load_secondary_index():
    with open("secondary_index.json", "r") as f:
        return json.load(f)

def tokenize_and_stem(query):
    # Tokenize and stem
    return processor._porter_stem(processor._tokenize(query))

def get_matching_docs_and_postings(main_indexfd, secondary_index, terms):

    # Return a dict of all the docs that contain all terms
    doc_sets = set()
    term_postings = {}
    first = True

    for term in terms:
        term_docs = set()

        # Seek to correct spot
        main_indexfd.seek(secondary_index[term], 0)
        line = main_indexfd.readline()

        # Add to dictionary
        term, postings = line.split(": ", 1)
        postings = ': '.join(postings.split("), ")).split(": ")
        for i in range(0, len(postings), 2):
            # Transform line to get the data we want
            url = postings[i][1:-1]
            posting = postings[i + 1].replace("Docinfo(", "")
            posting = posting.replace("wordfrequency=", "").replace("importance=", "").replace(")", "")

            # Add to the term doc set
            term_docs.add(url)

            # Add to the postings
            if term not in term_postings:
                term_postings[term] = {}
            term_postings[term][url] = [int(i) for i in posting.split(", ")]

        # If the first one, initialize doc_sets, otherwise intersection
        if first:
            doc_sets = term_docs
            first = False
        else:
            doc_sets = doc_sets.intersection(term_docs)

    return [doc_sets, term_postings]

# Search function
def search(query, main_indexfd, secondary_index, total_docs, doc_freqs, importance_boost=0.65, stop_threshold=0.34):

    # Process the query
    terms = tokenize_and_stem(query)

    # Check if the query is empty
    if not terms:
        return []

    # Count number of stopwords
    stopwords = 0
    for word in terms:
        if word in STOPS:
            stopwords += 1

    # If the ratio of stopwords in the query is under a certain threshold, they are not important
    # so remove them from the query for more accurate search
    stopwords = float(stopwords) / len(terms)
    if stopwords < stop_threshold:
        terms = [term for term in terms if term.lower() not in STOPS]

    # Check if terms exist in the index
    # Iterate over each stemmed term
    for term in terms:

        # Check if the term is present in the bookkeeping index
        if term not in secondary_index:

            # Return empty if any term is not found in the bookkeeping index
            # There are no documents containing all the terms
            return []

    # Get document lists for each term
    docs, term_postings_dict = get_matching_docs_and_postings(main_indexfd, secondary_index, terms)

    # If there were no documents found that had all terms, exit
    if len(docs) == 0:
        return []

    # Calculate importance scores for each document
    scores = []
    for doc in docs:
        score = 0.0

        for term in terms:
            # Retrieve term frequency (tf) and associate importance value for the term in the document from the index
            term_index = term_postings_dict[term]
            tf, importance = term_index[doc]

            # Calculate tf
            tf = float(tf) / doc_freqs[doc] * 100.0

            # Calculate idf
            idf = len(term_index)
            idf = math.log(total_docs / idf) if idf else 0

            # Calculate score
            term_score = tf * idf * (1 + importance_boost * importance)

            # Penalize excessively long or short files
            if doc_freqs[doc] > 10000 or doc_freqs[doc] < 200:
                term_score *= 0.60

            # Add the term's score to the document score
            score += term_score

        # Append scores
        scores.append((doc, score))

    # Return list in descending order
    return sorted(scores, key=lambda x: -x[1])

def main():

    start = time.time()
    # Load the document counts
    doc_freqs = load_doc_counts()
    num_docs = len(doc_freqs)

    # Load the bookkeeping index
    secondary_index = load_secondary_index()
    end = time.time()

    # Total usage: approx. 30 MB of main memory

    print(f"\nSearch initialized. Time elapsed: {1000 * (end - start)} ms.")

    # Open file descriptor for main index
    with open("data.json", "r") as main_indexfd:

        while True:
            # Ask for input
            query = input("\nEnter search query (enter '0' to quit): ").strip()
            if query == '0':
                break

            # Begin time
            start = time.time()

            # Retrieve search results
            results = search(query, main_indexfd, secondary_index, num_docs, doc_freqs)

            # End time
            end = time.time()

            # Print the top 5 URLs
            print(f"\nTop results for '{query}':")

            # Special case if no results found
            if len(results) == 0:
                print("No results found.")

            else:
                for i, (url, score) in enumerate(results[:10]):
                    print(f"{i + 1}. {url} (Score: {score:.2f})")
                    site = ai.Summarizer(url)
                    site.search_corpus()
                    response = site.query(query)
                    site.summarize(response)

            # Print time elapsed
            print(f"\nTime elapsed: {1000 * (end - start)} ms.")

if __name__ == "__main__":
    main()
