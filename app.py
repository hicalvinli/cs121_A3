import streamlit as st
from search import load_secondary_index, load_doc_counts, search
import time
import ai

secondary_index = load_secondary_index()
doc_counts = load_doc_counts()
num_docs = len(doc_counts)
st.markdown(
    """
    <style>

    .search-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .title {
        font-size: 80px;
        font-weight: bold;
        background: linear-gradient(to left, #ff9f9c, #058bf2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }

    .result-box {
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        width: 100%;
    }

    .text {
        color: #000000;
        text-align: center;
    }

    .result-url {
        color: #000000;
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    }

    .result-score {
        color: #000000;
        font-size: 0.9rem;
    }
    .result-summary {
        color: #333333;
        font-size: 1rem;
        margin-top 0.5rem;
    </style>
    """,
    unsafe_allow_html=True
)

# Main Content
with st.container():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<h1 class ="title">Welcome to CLAM</h1>', unsafe_allow_html=True)

    # Search component
    with st.form("search_form"):
        query = st.text_input(" ", placeholder="Enter Query", key="search_input")
        submitted = st.form_submit_button("Search")
    st.markdown('</div>', unsafe_allow_html=True)

# Handle Search
if submitted and query:
    start_time = time.time()
    with open("data.json", "r") as main_indexfd:
        results = search(query, main_indexfd, secondary_index, num_docs, doc_counts)
    execution_time = round((time.time() - start_time) * 1000, 2)

    # Display Results and Time
    st.subheader(f"Top Results for '{query}'")
    st.caption(f"Found {len(results)} results in {execution_time} ms")

    # Check if results were found
    if len(results) > 0:
        # Iterate over the top 5 results
        for i, (url, score) in enumerate(results[:10]):
            # Container for each result
            with st.container():
                st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
                # 10% for result number index, 90% for result details
                col1, col2 = st.columns([0.1, 0.9])
                # Display result number
                with col1:
                    st.markdown(f"{i + 1}")
                # Display URL & Score
                with col2:
                    st.markdown(f'<div class="result-url"><a href="{url}" target="_blank">{url}</a></div>',
                                unsafe_allow_html=True)
                    # AI Summary
                    # Retrieve and summarize site content for URL
                    summarizer = ai.Summarizer(url)
                    # Search corpus to retrieve raw content
                    summarizer.search_corpus()
                    # Generate summary
                    summarizer.query(query)
                    # Extract the summary text from API
                    summary_text = summarizer.response.text if summarizer.response else "Summary not available."
                    # Display summary
                    st.markdown(f'<div class ="result-summary">{summary_text}</div>', unsafe_allow_html=True)
                    st.markdown('<div>', unsafe_allow_html=True)

                    st.markdown(f'<div class="result-score">Relevance Score: {score:.2f}</div>', unsafe_allow_html=True)

    else:
        st.warning("No results found for your query")