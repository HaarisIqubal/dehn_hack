import streamlit as st
import pandas as pd
from ..tool.query_search import search_losungbib, sepearte_out_process, final_output

def setup_view():
    st.set_page_config(page_title="DHEN Smart Process Finder", page_icon="🔎", layout="wide")
    st.title("Search what process you want?")

    search_query = st.text_input("Search for the process ..", type="default")
    if st.button("Search"):
        if st.expander("Semantic Solutions ", expanded=False):
            losung_data = search_losungbib(search_query)
        if st.expander("Sorted Solution"):
            sorted_data = sepearte_out_process(losung_data)
        # Column mapping
        columns = [
            "Lfd. Nummer","Bauteilnamen", "Hersteller", "Typ", "Embedding_Values"
        ]
        # Convert to DataFrame
        df = pd.DataFrame(sorted_data, columns=columns)
        st.table(df)
        if st.button("Analyze"):
            if st.expander("Final Component List"):
                components_count = final_output()
                st.table(components_count)


