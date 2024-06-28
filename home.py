import streamlit as st
from streamlit_extras.grid import grid
from streamlit_option_menu import option_menu

import db
import startup_gui
import data_sources_gui
import insights_gui

db.init_db()

st.set_page_config(page_title = "IDEAS Startup Insights", layout = "wide")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

my_grid = grid([2, 22], [1, 5], 1, vertical_align="centre")

# Row 1 - Header:
my_grid.image('IDEAS-TIH.webp', width=100)
my_grid.title("IDEAS Startup Insights")

# Row 2:
with my_grid.container(height=640, border=True):  #Menu
    selected = option_menu(None, ["Startups", "Data Sources", "Extraction Profile", "Insights"],
                            icons=['building-up', 'archive', 'bookshelf', 'database'])

body = my_grid.container(height=640, border=True)  #Main body

# Row 3 - Footer:
my_grid.markdown("<h2 style='text-align: center; color: black;'> &#169;IDEAS-TIH </h2>", unsafe_allow_html=True)  #&#169; HTML code for copyright emoji


with body:
    if selected == "Startups":
        startup_gui.ingestion_gui()

    if selected == "Data Sources":
        data_sources_gui.sources_gui()

    if selected == "Extraction Profile":
        pass

    if selected == "Insights":
        insights_gui.insights_gui()
