import streamlit as st
from streamlit import session_state as ss


def HomeNav():
    st.sidebar.page_link("Centro_de_Control_Iaxxon_Energía.py", label="Home")


def LoginNav():
    st.sidebar.page_link("pages/account.py", label="Iaxxon Energía")


def Page1Nav():
    st.sidebar.page_link("pages/Estepa_Pabellon.py", label="Pabellon Estepa")


def Page2Nav():
    st.sidebar.page_link("pages/Estepa_Piscina.py", label="Piscina Estepa")

def Page3Nav():
    st.sidebar.page_link("pages/Estepa_Piscina.py", label="Colegio Do Brasil")

def Page4Nav():
    st.sidebar.page_link("pages/Estepa_Piscina.py", label="Campo de Fútbol Estepa")

def Page5Nav():
    st.sidebar.page_link("pages/Estepa_Piscina.py", label="Bodegas Habla")


def MenuButtons(user_roles=None):
    if user_roles is None:
        user_roles = {}

    if 'authentication_status' not in ss:
        ss.authentication_status = False

    # Always show the home and login navigators.
    HomeNav()
    LoginNav()

    # Show the other page navigators depending on the users' role.
    if ss["authentication_status"]:

        # (1) Only the admin role can access page 1 and other pages.
        # In a user roles get all the usernames with admin role.
        admins = [k for k, v in user_roles.items() if v == 'admin']
        estepa = [k for k, v in user_roles.items() if v == 'estepa']
        # Show page 1 if the username that logged in is an admin.
        if ss.username in admins:
            Page1Nav()
            Page2Nav()
            Page3Nav()
            Page4Nav()
            Page5Nav()
        elif ss.username in estepa:
            Page1Nav()
            Page2Nav()
