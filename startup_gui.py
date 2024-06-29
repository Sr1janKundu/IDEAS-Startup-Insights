# import os
# import time
import streamlit as st
import pandas as pd

import db


# def display_company_names(names):
#     '''
    
#     '''
#     st.header("Company Names in Database")
#     if names:
#         names_df = pd.DataFrame({'Company Names': names})
#         names_df.index = names_df.index + 1
#         with st.expander('Expand to see company names in database'):
#             st.table(names_df)

def display_company_names(names, search_button = False, search_query=None):
    '''
    Display the list of company names, optionally filtered by a search query.
    '''
    if search_query:
        names = [name for name in names if search_query.upper() in name]
    if names:
        names_df = pd.DataFrame({'Company Names': names})
        names_df.index = names_df.index + 1
        if search_query and search_button:
            st.table(names_df)
        else:
            with st.expander('Expand to see company names in database'):
                st.table(names_df)
    else:
        st.write("No company names found.")


def ingestion_gui():
    
    st.header("Company Names in Database")
    # Fetch and display updated list of company names
    updated_company_names = db.get_companies()
    # display_company_names(updated_company_names)

    search_query = st.text_input("Search for a company name")
    search_button = st.button("Search")
    display_company_names(updated_company_names, search_button, search_query)

    st.divider()
    new_company_name = st.text_input('Type-in company name (Do NOT use abbreviations such as "pvt." or  "ltd.")')
    if st.button('Upload company name') and new_company_name:
        new_company_name = new_company_name.upper()
        df = pd.DataFrame([new_company_name], columns=['Company Names'])
        db.insert_companies(df, 'Company Names')
        st.rerun()

    uploaded_file = st.file_uploader("Or upload CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        # If the uploaded file is an Excel file, convert it to CSV
        if uploaded_file.type=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        # company_column_name = 'Company Name'
        company_column_name = st.selectbox('Select company name column', df.columns.tolist(), index=None, placeholder='Select from menu')
        
        if st.button('Upload'):
            if company_column_name is not None:
                df[company_column_name] = df[company_column_name].str.upper()
                # Insert company names into the database
                db.insert_companies(df, company_column_name)
                st.rerun()
            else:
                st.error("Select Column!")



