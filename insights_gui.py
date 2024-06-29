import json
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

import db
import scrape
import io

# Function to truncate insights column
def truncate_insights(insights, length=100):
    if len(insights) > length:
        return insights[:length] + '...'
    else:
        return insights

def show_insights_table(df):
    df = df.reset_index()
    df.index = df.index + 1
    if not df.empty:
        df['insights'] = df['insights'].apply(lambda x: truncate_insights(x, 100))
        df['Select'] = False
        df = df.drop(['index', 'insights'], axis=1)
        st.write("## Insights in the database")
        edited_df = st.data_editor(df, hide_index=True, disabled=df.columns.drop('Select'))
        return edited_df
    else:
        st.write("No insights found in the database.")
        return pd.DataFrame()

def display_specific_insights(company_name, source_name, pdf_elements=None):
    insights_df = db.get_specific_insights(company_name, source_name)
    if not insights_df.empty:
        if source_name == 'Zauba Corp':
            for index, row in insights_df.iterrows():
                st.write(f"*Insight on **{company_name}** from **{source_name}** retrieved on **{row['date_created']}**:*")
                if pdf_elements is not None:
                    pdf_elements.append(Paragraph(f"Insight on {company_name} from {source_name} retrieved on {row['date_created']}:", getSampleStyleSheet()['Normal']))
                    pdf_elements.append(Spacer(1, 12))
                
                data = json.loads(row['insights'])
                st.subheader("Basic Information")
                st.write(data["Basic Information"])
                if pdf_elements is not None:
                    pdf_elements.append(Paragraph("Basic Information", getSampleStyleSheet()['Heading2']))
                    pdf_elements.append(Paragraph(data["Basic Information"], getSampleStyleSheet()['Normal']))
                    pdf_elements.append(Spacer(1, 12))
                
                st.subheader("Company Details")
                details_df = pd.DataFrame.from_dict(data["Company Details"], orient='index')
                details_df = details_df.reset_index()
                details_df.columns = ['Field', 'Data']
                details_df.index = details_df.index + 1
                st.dataframe(details_df, use_container_width=True)
                if pdf_elements is not None:
                    pdf_elements.append(Paragraph("Company Details", getSampleStyleSheet()['Heading2']))
                    table_data = [details_df.columns.tolist()] + details_df.values.tolist()
                    table = Table(table_data)
                    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                    pdf_elements.append(table)
                    pdf_elements.append(Spacer(1, 12))
                    
        elif source_name == 'Tofler':
            for index, row in insights_df.iterrows():
                st.write(f"*Insight on **{company_name}** from **{source_name}** retrieved on **{row['date_created']}**:*")
                if pdf_elements is not None:
                    pdf_elements.append(Paragraph(f"Insight on {company_name} from {source_name} retrieved on {row['date_created']}:", getSampleStyleSheet()['Normal']))
                    pdf_elements.append(Spacer(1, 12))
                    
                data = json.loads(row['insights'])
                st.subheader('Basic Information')
                st.write(data["Basic Information"])
                if pdf_elements is not None:
                    pdf_elements.append(Paragraph("Basic Information", getSampleStyleSheet()['Heading2']))
                    pdf_elements.append(Paragraph(data["Basic Information"], getSampleStyleSheet()['Normal']))
                    pdf_elements.append(Spacer(1, 12))
                
                st.subheader('Registration Details')
                reg_details_df = pd.DataFrame.from_dict(data["Registration Details"], orient='index')      
                reg_details_df = reg_details_df.reset_index()
                reg_details_df.columns = ['Field', 'Data']
                reg_details_df.index = reg_details_df.index + 1
                st.dataframe(reg_details_df, use_container_width=True)
                if pdf_elements is not None:
                    pdf_elements.append(Paragraph("Registration Details", getSampleStyleSheet()['Heading2']))
                    table_data = [reg_details_df.columns.tolist()] + reg_details_df.values.tolist()
                    table = Table(table_data)
                    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                    pdf_elements.append(table)
                    pdf_elements.append(Spacer(1, 12))
                    
                if data['Financials'] == 'Not available for free' or data['Financials'] == 'Not available':
                    break
                else:
                    st.subheader('Financials')
                    for point in data['Financials']['Brief Financial Report']:
                        st.markdown('- ' + point)
                    if pdf_elements is not None:
                        pdf_elements.append(Paragraph("Financials", getSampleStyleSheet()['Heading2']))
                        for point in data['Financials']['Brief Financial Report']:
                            pdf_elements.append(Paragraph('- ' + point, getSampleStyleSheet()['Normal']))
                        pdf_elements.append(Spacer(1, 12))
                        
                    remaining_financials = {k: v for k, v in data['Financials'].items() if k != 'Brief Financial Report'}
                    remaining_financials_df = pd.DataFrame.from_dict(remaining_financials, orient='index')
                    remaining_financials_df = remaining_financials_df.reset_index()
                    remaining_financials_df.columns = ['Field', 'Data']
                    remaining_financials_df.index = remaining_financials_df.index + 1
                    st.dataframe(remaining_financials_df, use_container_width=True)
                    if pdf_elements is not None:
                        table_data = [remaining_financials_df.columns.tolist()] + remaining_financials_df.values.tolist()
                        table = Table(table_data)
                        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                        pdf_elements.append(table)
                        pdf_elements.append(Spacer(1, 12))
                    
    else:
        st.error(f"No insights found for {company_name} from {source_name}.")

def insights_gui():
    st.header("Company Insights")
    df = db.get_insights_table()
    edited_df = show_insights_table(df)
    
    company_list = db.get_companies()
    source_df = pd.DataFrame(db.get_data_sources())
    source_list = source_df['sources']

    if df.empty:
        company_option1 = st.selectbox(
            label="Select Company",
            options=company_list,
            key='comp_opt_1',
            placeholder="Select company name to show insights",
            index=None
        )
        source_option1 = st.selectbox(
            label="Select Source", 
            options=source_list,
            key='source_opt_1',
            placeholder="Select source to retrieve insights from",
            index=0
        )
        if st.button("Get insights"):
            with st.spinner('Operation in progress. Please wait.'):
                source_url1 = db.get_source_url(source_option1)[0]
                scraped_data = scrape.scrape(company_option1, source_option1, source_url1)
                db.insert_insight(company_option1, source_option1, scraped_data)
            st.divider()
            display_specific_insights(company_option1, source_option1)
    else:
        show_selected = st.button("Show selected insights")
        st.divider()
        company_option1 = st.selectbox(
            label="Select Company",
            options=company_list,
            key='comp_opt_1',
            placeholder="Select company name to show insights",
            index=None
        )
        source_option1 = st.selectbox(
            label="Select Source", 
            options=source_list,
            key='source_opt_1',
            placeholder="Select source to retrieve insights from",
            index=0
        )
        if st.button("Get new insights"):
            with st.spinner('Operation in progress. Please wait.'):
                source_url1 = db.get_source_url(source_option1)[0]
                scraped_data = scrape.scrape(company_option1, source_option1, source_url1)
                db.insert_insight(company_option1, source_option1, scraped_data)
            st.divider()
            display_specific_insights(company_option1, source_option1)

        if show_selected:
            selected_rows = edited_df[edited_df['Select'] == True]
            if not selected_rows.empty:
                pdf_elements = []
                for idx, row in selected_rows.iterrows():
                    display_specific_insights(row['company_name'], row['source_name'], pdf_elements)
                st.session_state.pdf_elements = pdf_elements
            else:
                st.error("No rows selected")

        # if 'pdf_elements' in st.session_state:
        #     if st.button("Generate PDF"):
        #         buffer = io.BytesIO()
        #         doc = SimpleDocTemplate(buffer, pagesize=letter)
        #         doc.build(st.session_state.pdf_elements)
        #         buffer.seek(0)
        #         st.download_button(
        #             label="Download PDF",
        #             data=buffer,
        #             file_name="insights.pdf",
        #             mime="application/pdf"
        #         )
        if 'pdf_elements' in st.session_state and st.session_state.pdf_elements:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, title = "Report")
            doc.build(st.session_state.pdf_elements)
            buffer.seek(0)
            if st.download_button(
                label="Download as PDF",
                data=buffer,
                file_name="insights.pdf",
                mime="application/pdf"
            ):
                del st.session_state.pdf_elements
        




'''OLD CODE, WITHOUT DOWNLOAD BUTTON
import json
import pandas as pd
import streamlit as st
# import time 


import db
import scrape


# Function to truncate insights column
def truncate_insights(insights, length=100):
    if len(insights) > length:
        return insights[:length] + '...'
    else:
        return insights
    

# def show_insights_table(df):
#     df = df.reset_index()
#     df.index = df.index + 1
#     if not df.empty:
#         df['insights'] = df['insights'].apply(lambda x: truncate_insights(x, 100))
#         df = df.drop(['index', 'insights'], axis = 1)
#         st.write("## Insights in the database")
#         st.dataframe(df)
#     else:
#         st.write("No insights found in the database.")


def show_insights_table(df):
    df = df.reset_index()
    df.index = df.index + 1
    if not df.empty:
        df['insights'] = df['insights'].apply(lambda x: truncate_insights(x, 100))
        df['Select'] = False
        df = df.drop(['index', 'insights'], axis=1)
        st.write("## Insights in the database")
        edited_df = st.data_editor(df, hide_index=True, disabled=df.columns.drop('Select'))
        return edited_df
    else:
        st.write("No insights found in the database.")
        return pd.DataFrame()
    

# def show_insights_table(df):
#     df = df.reset_index(drop=True)
#     df.index = df.index + 1
#     if not df.empty:
#         df['insights'] = df['insights'].apply(lambda x: truncate_insights(x, 100))
#         df = df.drop(['insights'], axis=1)
#         st.write("## Insights in the database")
        
#         # Create a radio button for selection
#         selected_index = st.radio("Select a row", options=df.index, format_func=lambda x: f"Row {x+1}")
        
#         # Display the dataframe
#         st.dataframe(df)
        
#         return df, selected_index
#     else:
#         st.write("No insights found in the database.")
#         return pd.DataFrame(), None

def display_specific_insights(company_name, source_name):
    insights_df = db.get_specific_insights(company_name, source_name)
    if not insights_df.empty:
        if source_name == 'Zauba Corp':
            for index, row in insights_df.iterrows():
                st.write(f"*Insight on **{company_name}** from **{source_name}** retrieved on **{row['date_created']}**:*")
                # st.json(row['insights'])
                data = json.loads(row['insights'])
                st.subheader("Basic Information")
                st.write(data["Basic Information"])
                st.subheader("Company Details")
                details_df = pd.DataFrame.from_dict(data["Company Details"], orient='index')
                details_df = details_df.reset_index()
                details_df.columns = ['Field', 'Data']
                details_df.index = details_df.index+1
                st.dataframe(details_df, use_container_width=True)
        elif source_name == 'Tofler':
            for index, row in insights_df.iterrows():
                st.write(f"*Insight on **{company_name}** from **{source_name}** retrieved on **{row['date_created']}**:*")
                # st.json(row['insights'])
                data = json.loads(row['insights'])
                st.subheader('Basic Information')
                st.write(data["Basic Information"])
                st.subheader('Registration Details')
                reg_details_df = pd.DataFrame.from_dict(data["Registration Details"], orient='index')      
                reg_details_df = reg_details_df.reset_index()
                reg_details_df.columns = ['Field', 'Data']
                reg_details_df.index = reg_details_df.index+1
                st.dataframe(reg_details_df, use_container_width=True)
                # st.subheader('Financials')
                # for point in data['Financials']['Brief Financial Report']:
                #     st.markdown('- '+point)
                # remaining_financials = {k: v for k, v in data['Financials'].items() if k != 'Brief Financial Report'}
                # remaining_financials_df = pd.DataFrame.from_dict(remaining_financials, orient='index')
                # remaining_financials_df = remaining_financials_df.reset_index()
                # remaining_financials_df.columns = ['Field', 'Data']
                # remaining_financials_df.index = remaining_financials_df.index+1
                # st.dataframe(remaining_financials_df, use_container_width=True)  
                if data['Financials'] == 'Not available for free':
                    break
                else:
                    st.subheader('Financials')
                    for point in data['Financials']['Brief Financial Report']:
                        st.markdown('- '+point)
                    remaining_financials = {k: v for k, v in data['Financials'].items() if k != 'Brief Financial Report'}
                    remaining_financials_df = pd.DataFrame.from_dict(remaining_financials, orient='index')
                    remaining_financials_df = remaining_financials_df.reset_index()
                    remaining_financials_df.columns = ['Field', 'Data']
                    remaining_financials_df.index = remaining_financials_df.index+1
                    st.dataframe(remaining_financials_df, use_container_width=True)                

    else:
        st.error(f"No insights found for {company_name} from {source_name}.")


# def insights_gui():
#     st.header("Company Insights")
#     df = db.get_insights_table()
#     show_insights_table(df)
    
#     st.divider()
#     company_list = db.get_companies()
#     source_df = pd.DataFrame(db.get_data_sources())
#     source_list = source_df['sources']
#     if df.empty:
#         # st.dataframe(df)
#         company_option1 = st.selectbox(
#             label="Select Company",
#             options=company_list,
#             key='comp_opt_1',
#             placeholder="Select company name to show insights",
#             index=None
#         )
#         source_option1 = st.selectbox(
#             label="Select Source", 
#             options=source_list,
#             key='source_opt_1',
#             placeholder="Select source to retrieve insights from",
#             index=0
#         )
#         if st.button("Get insights"):
#             #tick = time.time()
#             #st.write(company_option1, source_option1)
#             #st.json(scraped_data)
#             #st.rerun()
#             with st.spinner('Operation in progress. Please wait.'):
#                 source_url1 = db.get_source_url(source_option1)[0]
#                 scraped_data = scrape.scrape(company_option1, source_option1, source_url1)
#                 db.insert_insight(company_option1, source_option1, scraped_data)
#             st.divider()
#             display_specific_insights(company_option1, source_option1)
#             #tock = time.time()
#             #st.write(tock - tick)
#     else:
#         col1, col2 = st.columns(2)
#         with col1:
#             company_option1 = st.selectbox(
#                 label="Select Company",
#                 options=company_list,
#                 key='comp_opt_1',
#                 placeholder="Select company name to show insights",
#                 index=None
#             )
#             source_option1 = st.selectbox(
#                 label="Select Source", 
#                 options=source_list,
#                 key='source_opt_1',
#                 placeholder="Select source to retrieve insights from",
#                 index=0
#             )
#             get_ins = st.button("Get insights")


#         with col2:
#             company_list_in_insights_table = set(db.get_company_list_from_insights_table())
#             company_option2 = st.selectbox(
#                 label="Select Company",
#                 options=company_list_in_insights_table,
#                 key='comp_opt_2',
#                 placeholder="Select company name to show insights",
#                 index=0
#             )
#             source_option2 = st.selectbox(
#                 label="Select Source", 
#                 options=source_list,
#                 key='source_opt_2',
#                 placeholder="Select source to retrieve insights from",
#                 index=0
#             )
#             show_ins = st.button("Show insights")

#         if get_ins:
#             #tick = time.time()
#             #st.write(company_option1, source_option1)
#             #st.json(scraped_data)
#             #st.rerun()
#             with st.spinner('Operation in progress. Please wait.'):
#                 source_url1 = db.get_source_url(source_option1)[0]
#                 # st.write(source_url1)
#                 scraped_data = scrape.scrape(company_option1, source_option1, source_url1)
#                 db.insert_insight(company_option1, source_option1, scraped_data)
#             st.divider()
#             display_specific_insights(company_option1, source_option1)
#             #tock = time.time()
#             #st.write(tock - tick)

#         elif show_ins:
#             #tick = time.time()
#             #st.json(scraped_data)
#             #st.rerun()
#             with st.spinner('Operation in progress. Please wait.'):
#                 st.divider()
#                 display_specific_insights(company_option2, source_option2)
#             #tock = time.time()
#             #st.write(tock - tick)



def insights_gui():
    st.header("Company Insights")
    df = db.get_insights_table()
    edited_df = show_insights_table(df)
    
    company_list = db.get_companies()
    source_df = pd.DataFrame(db.get_data_sources())
    source_list = source_df['sources']

    if df.empty:
        # Your existing code for when df is empty
        company_option1 = st.selectbox(
            label="Select Company",
            options=company_list,
            key='comp_opt_1',
            placeholder="Select company name to show insights",
            index=None
        )
        source_option1 = st.selectbox(
            label="Select Source", 
            options=source_list,
            key='source_opt_1',
            placeholder="Select source to retrieve insights from",
            index=0
        )
        if st.button("Get insights"):
            with st.spinner('Operation in progress. Please wait.'):
                source_url1 = db.get_source_url(source_option1)[0]
                scraped_data = scrape.scrape(company_option1, source_option1, source_url1)
                db.insert_insight(company_option1, source_option1, scraped_data)
            st.divider()
            display_specific_insights(company_option1, source_option1)
    else:
        show_selected = st.button("Show selected insights")
        st.divider()    
        company_option1 = st.selectbox(
            label="Select Company",
            options=company_list,
            key='comp_opt_1',
            placeholder="Select company name to show insights",
            index=None
        )
        source_option1 = st.selectbox(
            label="Select Source", 
            options=source_list,
            key='source_opt_1',
            placeholder="Select source to retrieve insights from",
            index=0
        )
        get_ins = st.button("Get insights")


        if get_ins:
            with st.spinner('Operation in progress. Please wait.'):
                source_url1 = db.get_source_url(source_option1)[0]
                scraped_data = scrape.scrape(company_option1, source_option1, source_url1)
                db.insert_insight(company_option1, source_option1, scraped_data)
            st.divider()
            display_specific_insights(company_option1, source_option1)

        elif show_selected:
            # selected_row = edited_df[edited_df['Select']].iloc[0]
            # company_name = selected_row['company_name']
            # source_name = selected_row['source_name']
            # with st.spinner('Operation in progress. Please wait.'):
            #     st.divider()
            #     display_specific_insights(company_name, source_name)
            selected_rows = edited_df[edited_df['Select']]
            for _, row in selected_rows.iterrows():
                company_name = row['company_name']
                source_name = row['source_name']
                with st.spinner('Operation in progress. Please wait.'):
                    st.divider()
                    display_specific_insights(company_name, source_name)
                    st.divider()
'''
