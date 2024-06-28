#import os
import logging
import duckdb
import pandas as pd
import streamlit as st


def init_db():
    '''
    
    '''
    connection = None
    try:
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        
        if 'connection' not in st.session_state:
            # Connect to the DuckDB database
            connection = duckdb.connect("startupinsight_db.db")
            st.session_state['connection'] = connection

            # Create sequences for use as primary keys
            logging.info("Creating sequences if they do not exist.")
            connection.execute('CREATE SEQUENCE IF NOT EXISTS "seq_company_id" START 1')
            connection.execute('CREATE SEQUENCE IF NOT EXISTS "seq_data_source_id" START 1')
            connection.execute('CREATE SEQUENCE IF NOT EXISTS "seq_insights_id" START 1')

            # Create tables if they do not exist
            logging.info("Creating tables if they do not exist.")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    company_id INTEGER PRIMARY KEY DEFAULT nextval('seq_company_id'), 
                    company_name VARCHAR(1000) UNIQUE, 
                    company_url VARCHAR(5000) UNIQUE, 
                    date_created DATETIME, 
                    description VARCHAR(50000)
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS data_sources (
                    source_id INTEGER PRIMARY KEY DEFAULT nextval('seq_data_source_id'), 
                    source_name VARCHAR(1000) UNIQUE, 
                    source_url VARCHAR(5000) UNIQUE, 
                    date_created DATETIME, 
                    description VARCHAR(50000)
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS insights (
                    insight_id INTEGER PRIMARY KEY DEFAULT nextval('seq_insights_id'), 
                    company_id INTEGER, 
                    source_id INTEGER, 
                    date_created DATETIME, 
                    insights JSON, 
                    description VARCHAR(50000), 
                    FOREIGN KEY (company_id) REFERENCES companies (company_id), 
                    FOREIGN KEY (source_id) REFERENCES data_sources (source_id)
                )
            """)

            logging.info("Database initialization completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during database initialization: {e}")

    # finally:
    #     # Ensure the connection is closed properly when the session ends
    #     @st.on_session_end
    #     def close_connection():
    #         if 'connection' in st.session_state:
    #             connection = st.session_state.pop('connection')
    #             connection.close()
    #             logging.info("Database connection closed.")


def insert_companies(df, company_col_name):
    '''
    
    '''

    # Ensure the database is initialized and connected
    if 'connection' not in st.session_state:
        init_db() 
    
    connection = st.session_state['connection']

    logging.basicConfig(level=logging.INFO)
    
    # Prepare a query to check for the existence of a company name
    check_query = "SELECT COUNT(*) FROM companies WHERE company_name = ?"
    # Prepare an insert query
    insert_query = "INSERT INTO companies (company_name, date_created) VALUES (?, get_current_timestamp())"
    
    for company_name in df[company_col_name]:
        # Check if the company already exists
        logging.info(f"Checking if {company_name} already exists in companies table.")
        result = connection.execute(check_query, [str(company_name)]).fetchone()
        if result[0] == 0:  # If the company does not exist
            # Insert the new company
            connection.execute(insert_query, [str(company_name)])
            #print(f"Inserted company: {company_name}")
            logging.info(f"{company_name} successfully inserted in companies table.")
        else:
            pass
            #print(f"Skipped existing company: {company_name}")
            logging.info(f"{company_name} already there in companies table, skipping.")


def insert_data_sources(df, name_col, url_col):
    '''
    
    '''
    # Ensure the database is initialized and connected
    if 'connection' not in st.session_state:
        init_db()  
    
    connection = st.session_state['connection']
    
    # Prepare a query to check for the existence of a source name
    check_query = "SELECT COUNT(*) FROM data_sources WHERE source_name = ?"
    # Prepare an insert query
    insert_query = "INSERT INTO data_sources (source_name, source_url, date_created) VALUES (?, ?, get_current_timestamp())"
    
    for index, row in df.iterrows():
        source_name = row[name_col]
        source_url = row[url_col]
        
        # Check if the source already exists
        result = connection.execute(check_query, [source_name]).fetchone()
        if result[0] == 0:  # If the source does not exist
            # Insert the new source with the current date and time
            #current_datetime = datetime.now()
            connection.execute(insert_query, [source_name, source_url])
            #print(f"Inserted source: {source_name}")
        else:
            pass
            #print(f"Skipped existing source: {source_name}")


def get_source_url(source_name):
    '''
    
    '''
    # Ensure the database is initialized and connected
    if 'connection' not in st.session_state:
        init_db()  
    
    connection = st.session_state['connection']

    query = "SELECT source_url FROM data_sources WHERE source_name = ?"

    result = connection.execute(query, [source_name]).fetchone()

    return result

# def insert_insight(company_name, source_name, insights_json):
#     '''
    
#     '''
#     # Ensure the database is initialized and connected
#     if 'connection' not in st.session_state:
#         init_db()  
    
#     connection = st.session_state['connection']

#     # Prepare queries to get the company_id and source_id
#     get_company_id_query = "SELECT company_id FROM companies WHERE company_name = ?"
#     get_source_id_query = "SELECT source_id FROM data_sources WHERE source_name = ?"
    
#     # Fetch company_id
#     company_result = connection.execute(get_company_id_query, [company_name]).fetchone()
#     if company_result is None:
#         print(f"Company '{company_name}' not found.")
#         return
#     company_id = company_result[0]

#     # Fetch source_id
#     source_result = connection.execute(get_source_id_query, [source_name]).fetchone()
#     if source_result is None:
#         print(f"Source '{source_name}' not found.")
#         return
#     source_id = source_result[0]
    
#     # Prepare the insert query for the insights table
#     insert_insight_query = """
#         INSERT INTO insights (company_id, source_id, date_created, insights, description) 
#         VALUES (?, ?, ?, ?, ?)
#     """
    
#     # Current date and time
#     current_datetime = datetime.now()
    
#     # Insert the new insight
#     connection.execute(insert_insight_query, [company_id, source_id, current_datetime, insights_json, ""])
#     #print(f"Inserted insight for company '{company_name}' from source '{source_name}'.")


def insert_insight(company_name, source_name, insights_json):
    '''
    
    '''
    # Ensure the database is initialized and connected
    if 'connection' not in st.session_state:
        init_db()  
    
    connection = st.session_state['connection']

    logging.basicConfig(level=logging.INFO)

    # Prepare queries to get the company_id and source_id
    get_company_id_query = "SELECT company_id FROM companies WHERE company_name = ?"
    get_source_id_query = "SELECT source_id FROM data_sources WHERE source_name = ?"
    
    # Fetch company_id
    company_result = connection.execute(get_company_id_query, [company_name]).fetchone()
    if company_result is None:
        print(f"Company '{company_name}' not found.")
        return
    company_id = company_result[0]

    # Fetch source_id
    source_result = connection.execute(get_source_id_query, [source_name]).fetchone()
    if source_result is None:
        print(f"Source '{source_name}' not found.")
        return
    source_id = source_result[0]
    
    # Prepare a query to check for existing insights
    check_insight_query = "SELECT insight_id FROM insights WHERE company_id = ? AND source_id = ?"
    
    # Check if the insight already exists
    insight_result = connection.execute(check_insight_query, [company_id, source_id]).fetchone()
    
    # Current date and time
    #current_datetime = datetime.now()
    
    if insight_result is None:
        # Prepare the insert query for the insights table
        insert_insight_query = """
            INSERT INTO insights (company_id, source_id, date_created, insights, description) 
            VALUES (?, ?, get_current_timestamp(), ?, ?)
        """
        # Insert the new insight
        connection.execute(insert_insight_query, [company_id, source_id, insights_json, ""])
        print(f"Inserted new insight for company '{company_name}' from source '{source_name}'.")
    else:
        # Prepare the update query for the insights table
        update_insight_query = """
            UPDATE insights 
            SET date_created = get_current_timestamp(), insights = ? 
            WHERE insight_id = ?
        """
        # Update the existing insight
        insight_id = insight_result[0]
        connection.execute(update_insight_query, [insights_json, insight_id])
        print(f"Updated existing insight for company '{company_name}' from source '{source_name}'.")


def get_companies():
    '''
    Function to fetch companies from the companies table of the database
    '''
    connection = st.session_state['connection']
    query = "SELECT company_name FROM companies"
    result = connection.execute(query).fetchall()
    companies = [row[0] for row in result]
    companies = [company for company in companies if company == company]   # remove nan values
    companies.sort()

    return companies


def get_data_sources():
    '''
    Function to fetch data sources from the data_sources table of the database
    '''
    connection = st.session_state['connection']
    query = "SELECT source_name, source_url FROM data_sources"
    result = connection.execute(query).fetchall()
    if result:
        data_sources = [{"sources": row[0], "url": row[1]} for row in result]
        return data_sources
    else:
        return None


def get_insights_table():
    '''
    
    '''
    # Ensure the database is initialized and connected
    if 'connection' not in st.session_state:
        init_db()  # Call your init_db function to initialize the DB

    connection = st.session_state['connection']

    # Query to fetch all data from the insights table along with company name and source name
    query = """
        SELECT 
            c.company_name, 
            d.source_name, 
            i.date_created, 
            i.insights, 
            i.description
        FROM insights i
        JOIN companies c ON i.company_id = c.company_id
        JOIN data_sources d ON i.source_id = d.source_id
    """
    
    # Execute the query and fetch all results
    result = connection.execute(query).fetchall()
    
    # Check if any data is fetched
    if result:
        # Get the column names from the query result
        columns = [desc[0] for desc in connection.description]
        
        # Convert the result into a DataFrame
        insights_df = pd.DataFrame(result, columns=columns).sort_values(by=['company_name'], ascending=True)
        return insights_df
    else:
        return pd.DataFrame() 


def get_specific_insights(company_name, source_name):
    '''
    
    '''
    # Ensure the database is initialized and connected
    if 'connection' not in st.session_state:
        init_db()  # Call your init_db function to initialize the DB

    connection = st.session_state['connection']

    # Query to fetch data from the insights column and date_created column for the specified company_name and source_name
    query = """
        SELECT i.insights, i.date_created
        FROM insights i
        JOIN companies c ON i.company_id = c.company_id
        JOIN data_sources d ON i.source_id = d.source_id
        WHERE c.company_name = ? AND d.source_name = ?
    """

    # Execute the query with the provided company_name and source_name
    result = connection.execute(query, [company_name, source_name]).fetchall()

    # Check if any data is fetched
    if result:
        # Get the column names from the query result
        columns = [desc[0] for desc in connection.description]

        # Convert the result into a DataFrame
        insights_df = pd.DataFrame(result, columns=columns)
        return insights_df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data is found
    

def get_company_list_from_insights_table():
    '''
    
    '''
    # Ensure the database is initialized and connected
    if 'connection' not in st.session_state:
        init_db()  # Call your init_db function to initialize the DB

    connection = st.session_state['connection']

    # Query to fetch data from the insights column and date_created column for the specified company_name and source_name
    query = """
        SELECT c.company_name as company_name
        FROM insights i
        JOIN companies c ON i.company_id = c.company_id
    """

    # Execute the query with the provided company_name and source_name
    result = connection.execute(query).fetchall()

    company_names = [row[0] for row in result]
    company_names.sort()
    return company_names