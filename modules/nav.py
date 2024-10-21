import streamlit as st
from streamlit import session_state as ss
from Centro_de_Control_Iaxxon_Energía import show_page as Iaxxon_Energia_show_page

# Importar los diferentes módulos de página
from pages import Estepa_Pabellon, Estepa_Piscina, colegiodobrasil, bodegashabla, campofutbol_estepa, duplex, huetorvega_pabellon, pabellon_aguilar, piscina_pedrera, piscina_priego, Toyota_Hispaljarafe

def MenuButtons(user_roles=None):
    if user_roles is None:
        user_roles = {}

    if 'authentication_status' not in ss:
        ss.authentication_status = False

    # Siempre muestra la página de inicio
    pages = {"Iaxxon Energía": Iaxxon_Energia_show_page}

    if ss["authentication_status"]:
        # Define los roles y las páginas que pueden acceder
        role_pages = {
            'admin': {
                "Pabellon Estepa": Estepa_Pabellon.show_page,
                "Piscina Estepa": Estepa_Piscina.show_page,
                "Colegio Do Brasil": colegiodobrasil.show_page,
                "Piscina Pedrera": piscina_pedrera.show_page,
                "Toyota Hispaljarafe": Toyota_Hispaljarafe.show_page
            },
            'estepa': {
                "Pabellon Estepa": Estepa_Pabellon.show_page,
                "Piscina Estepa": Estepa_Piscina.show_page,
                "Campo de Fútbol Estepa": Estepa_CampoFutbol.show_page
            }
            # Agrega otros roles y sus páginas correspondientes aquí
        }

        # Obtener el rol del usuario actual
        user_role = user_roles.get(ss.username)

        # Agregar páginas según el rol del usuario
        if user_role in role_pages:
            pages.update(role_pages[user_role])

    # Crear el menú de navegación en la barra lateral
    selection = st.sidebar.selectbox("Seleccione una página", list(pages.keys()))
    selected_page = pages[selection]

    # Ejecutar la página seleccionada
    selected_page()  # Cada página ahora es una función
       