import time
from flask import Flask, render_template, request
from search import load_secondary_index, load_doc_counts, search


app = Flask(__name__)

# Load indexes
secondary_index = load_secondary_index()
doc_counts = load_doc_counts()
num_docs = len(doc_counts)

@app.route("/", methods = ["GET", "POST"])
def index_page():
    query = ""
    results = []
    exec_time = None

    #Check if form is submitted
    if request.method == "POST":
        # Get search query from form data
        query = request.form.get("query", "")
        # Perform search if query is not empty
        if query:
            start_time = time.time()
            with open("data.json", "r") as main_indexfd:
                results = search(query, main_indexfd, secondary_index, num_docs, doc_counts)
            exec_time = round((time.time() - start_time) * 1000, 2)

    # Render the index.html
    return render_template("index.html", results=results, query=query, exec_time=exec_time)

# Start Flask Web Server
if __name__ == "__main__":
    app.run(debug=True)