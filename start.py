import streamlit as st
from streamlit_option_menu import option_menu
import main as home
import website

sel = option_menu(None, ["Video AI","Website AI"], 
    icons=['robot','robot'], menu_icon="cast", default_index=0,
    orientation="horizontal",
    styles={
            "container": {"padding": "0!important", "background-color": "black"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "14px", "margin":"0px", "--hover-color": "#686D76"},
            "nav-link-selected": {"background-color": "#444444"},
    } 
)
if sel == "Video AI":
    home.main()
elif sel == "Website AI":
    website.main()