import streamlit as st
from ..tool.query_search import search_losungbib, sepearte_out_process

def setup_view():
    st.set_page_config(page_title="DHEN Smart Process Finder", page_icon="🔎", layout="wide")
    st.title("Search what process you want?")

    search_query = st.text_input("Search for the process ..", type="default")
    if st.button("Search"):
        losung_data = search_losungbib(search_query)
        sorted_data = sepearte_out_process(losung_data)
        print(sorted_data)


