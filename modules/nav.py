import streamlit as st
from streamlit import session_state as ss


def HomeNav():
    st.sidebar.page_link("Centro_de_Control_Iaxxon_Energía.py", label="Iaxxon Energía")

def Page1Nav():
    st.sidebar.page_link("pages/Estepa_Pabellon.py", label="Pabellon Estepa")

def Page2Nav():
    st.sidebar.page_link("pages/Estepa_Piscina.py", label="Piscina Estepa")

def Page3Nav():
    st.sidebar.page_link("pages/colegiodobrasil.py", label="Colegio Do Brasil")

def Page4Nav():
    st.sidebar.page_link("pages/campofutbol_estepa.py", label="Campo de Fútbol Estepa")

def Page5Nav():
    st.sidebar.page_link("pages/bodegashabla.py", label="Bodegas Habla")

def Page6Nav():
    st.sidebar.page_link("pages/duplex.py", label="Duplex")

def Page7Nav():
    st.sidebar.page_link("pages/piscina_priego.py", label="Piscina Priego de Córdoba")

def Page8Nav():
    st.sidebar.page_link("pages/pabellon_aguilar.py", label="Pabellón Aguilar de la Ftra.")

def Pag9Nav():
    st.sidebar.page_link("pages/huetorvega_pabellon.py", label="Pabellón Huétor Vega")




def MenuButtons(user_roles=None):
    if user_roles is None:
        user_roles = {}

    if 'authentication_status' not in ss:
        ss.authentication_status = False

    # Always show the home navigator.
    HomeNav()

    # Show the other page navigators depending on the users' role.
    if ss["authentication_status"]:

        # (1) Only the admin role can access page 1 and other pages.
        # In a user roles get all the usernames with admin role.
        admins = [k for k, v in user_roles.items() if v == 'admin']
        estepa = [k for k, v in user_roles.items() if v == 'estepa']
        duplex = [k for k, v in user_roles.items() if v == 'duplex']
        colegiodobrasil = [k for k, v in user_roles.items() if v == 'colegiodobrasil']
        aguilardelafrontera = [k for k, v in user_roles.items() if v == 'aguilardelafrontera']
        priegodecordoba = [k for k, v in user_roles.items() if v == 'priegodecordoba']
        bodegashabla = [k for k, v in user_roles.items() if v == 'bodegashabla']
        huetorvega = [k for k, v in user_roles.items() if v == 'huetorvega']


        # Show page 1 if the username that logged in is an admin.
        if ss.username in admins:
            Page1Nav()
            Page2Nav()
            Page3Nav()
            Page4Nav()
            Page5Nav()
            Page6Nav()
            Page7Nav()
            Page8Nav()
            Page9Nav()
        elif ss.username in estepa:
            Page1Nav()
            Page2Nav()
            Page4Nav()
        elif ss.username in duplex:
            Page6Nav()
        elif ss.username in colegiodobrasil:
            Page3Nav()
        elif ss.username in aguilardelafrontera:
            Page8Nav()
        elif ss.username in priegodecordoba:
            Page7Nav()
        elif ss.username in bodegashabla:
            Page5Nav()
        elif ss.username in huetorvega:
            Page9Nav()

