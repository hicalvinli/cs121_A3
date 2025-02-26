import streamlit as st


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

st.markdown('<div class="centered">', unsafe_allow_html = True)

query = st.text_input(" ", placeholder = "Query Here.")
st.markdown('<h1 class="title">Welcome to CLAM.</h1>', unsafe_allow_html = True)

st.markdown('</div>', unsafe_allow_html = True)
