import streamlit as st
from search import load_index_and_metadata, search
import time

#Load search index and metadata
@st.cache_resource
def load_data():
    return load_index_and_metadata()
index, total_docs = load_data()

st.markdown(

    """
    <style>
    .centered {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .title {
        font-size: 80px;
        background: linear-gradient(to right, #ff9f9c, #058bf2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }

    .text {
        text-align: center;
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
