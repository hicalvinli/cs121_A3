import time
from app2 import flask, render_template, request
import search

app = Flask(__name__)

# Load indexes
index, total_docs = load_index_and_metadata()
doc_counts = load_doc_counts()

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
            results = search(query, index, total_docs, doc_counts)
            exec_time = round((time.time() - start_time) * 1000, 2)

    # Render the index.html
    return render_template("index.html", results=results, query=query, exec_time=exec_time)

# Start Flask Web Server
if __name__ == "__main__":
    app.run(debug=True)