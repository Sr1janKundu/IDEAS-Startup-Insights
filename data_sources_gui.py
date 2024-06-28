import streamlit as st
import pandas as pd

import db


def display_data_sources(sources):
    '''
    
    '''
    st.header("Data Sources in Database")
    if sources:
        sources_df = pd.DataFrame(sources)
        sources_df.index = sources_df.index + 1
        st.table(sources_df)


def sources_gui():
    # Fetch and display updated list of source names and source urls
    updated_source_names = db.get_data_sources()
    display_data_sources(updated_source_names)

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        # If the uploaded file is an Excel file, convert it to CSV
        if uploaded_file.type=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':    
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)

        col1, col2 = st.columns(2)
        with col1:
            # source_name_column = 'Sources'
            source_name_column = st.selectbox('Select source name column', df.columns.tolist(), index=None, placeholder='Select from menu')
        with col2:
            # source_url_column = 'url'
            source_url_column = st.selectbox('Select source url column', df.columns.tolist(), index=None, placeholder='Select from menu')
        
        if st.button('Upload'):    
            if source_name_column is not None and source_url_column is not None:
                # Insert source names and source URLs into the database
                db.insert_data_sources(df, source_name_column, source_url_column)
                st.rerun()
            else:
                st.error("Select Columns!")