import pandas as pd 
import streamlit as st
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.utils import fetch_collection_from_cloud

mongo_con= MongoIO()





def Easy_Summary(paragraph : str):
    print('summary')















try:
    st.write('started summarize')
    st.write(st.session_state.chosen_text)
    st.write(st.session_state.chosen_title)
    
        

   
    with st.sidebar:
            st.markdown("""
            No Data Available for summary. Please Go to search page for analysis.
            """)
except AttributeError:
    product_name = None
    st.markdown(""" # No Data Available for analysis.""")
