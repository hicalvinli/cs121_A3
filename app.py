import streamlit as st
from search import load_index_and_metadata, load_doc_counts, search
import time

index, total_docs = load_index_and_metadata()
doc_counts = load_doc_counts()
st.markdown(
    """
    <style>

    @keyframes gradientAnimation {
        0% {
            background-position: 100% 50%;
        }
        100% {
            background-position: -33% 50%;
        }
    }
    
    .centered {
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
        text-align: center;
    }
    
    .result-url {
        color: white;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .result-score {
        color: white;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html = True
)

#Main Content
with st.container():
    st.markdown('<div class="centered">', unsafe_allow_html = True)
    st.markdown('<h1 class ="title">Welcome to CLAM</h1>', unsafe_allow_html = True)

    #Search component
    with st.form("search_form"):
        query = st.text_input(" ", placeholder = "Enter Query", key="search_input")
        submitted = st.form_submit_button("Search")
    st.markdown('</div>', unsafe_allow_html = True)

#Handle Search
if submitted and query:
    start_time = time.time()
    results = search(query, index, total_docs, doc_counts)
    execution_time = round((time.time() - start_time) * 1000, 2)

    #Display Results and Time
    st.subheader(f"Top Results for '{query}'")
    st.caption(f"Found {len(results)} results in {execution_time} ms")

    #Check if results were found
    if len(results) > 0:
        #Iterate over the top 5 results
        for i, (url, score) in enumerate(results[:5]):
            #Container for each result
            with st.container():
                st.markdown(f'<div class="result-box">', unsafe_allow_html=True)
                #10% for result number index, 90% for result details
                col1, col2 = st.columns([0.1, 0.9])
                #Display result number
                with col1:
                    st.markdown(f"{i+1}")
                #Display URL & Score
                with col2:
                    st.markdown(f'<div class="result-url">{url}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="result_score">Relevance Score: {score:.2f}</div>', unsafe_allow_html=True)
                    st.markdown('<div>', unsafe_allow_html=True)
    else:
        st.warning("No results found for your query")