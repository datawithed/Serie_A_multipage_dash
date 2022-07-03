# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 12:35:12 2022

@author: Ed.Morris
"""

# import modules
import streamlit as st
from PIL import Image

# ==========================================================
# Dashboard configuration
# ==========================================================
st.set_page_config(page_title = 'Intro', page_icon = Image.open('Serie_A_logo.jpg'), initial_sidebar_state = 'expanded')

st.sidebar.success('Select an analysis above.')

st.header("""
         Serie A Match Analysis: Juventus 3 - 0 Sampdoria (10/09/2020)
         \n By Ed Morris
         """)
st.markdown("""
            - This is a brief dashboard demonstrating manipulation and data visualisations using free Wyscout event data for the Serie A match Juventus - Sampdoria on 10th September 2020.
            - Here, I hope to demonstrate my ability to use this event data to create visually appealing graphics that can be used to analyse individual player performance, team performance and provide data-driven metrics where appropriate.
            - The data used for this can be found here: https://footballdata.wyscout.com/download-samples/
            """)
            
