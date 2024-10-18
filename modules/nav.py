import streamlit as st
from streamlit import session_state as ss

def MenuButtons(user_roles=None):
    if user_roles is None:
        user_roles = {}

    if 'authentication_status' not in ss:
        ss.authentication_status = False

    # Siempre muestra la página de inicio
    pages = {"Iaxxon Energía": "Centro_de_Control_Iaxxon_Energía.py"}

    if ss["authentication_status"]:
        # Define los roles y las páginas que pueden acceder
        role_pages = {
            'admin': {
                "Pabellon Estepa": "pages/Estepa_Pabellon.py",
                "Piscina Estepa": "pages/Estepa_Piscina.py",
                "Colegio Do Brasil": "pages/colegiodobrasil.py",
                "Campo de Fútbol Estepa": "pages/campofutbol_estepa.py",
                "Duplex": "pages/duplex.py",
                "Piscina Priego de Córdoba": "pages/piscina_priego.py",
                "Pabellón Aguilar de la Ftra.": "pages/pabellon_aguilar.py",
                "Pabellón Huétor Vega": "pages/huetorvega_pabellon.py",
                "Toyota Hispaljarafe": "pages/Toyota_Hispaljarafe.py",
                "Piscina Pedrera": "pages/piscina_pedrera.py"
            },
            'estepa': {
                "Pabellon Estepa": "pages/Estepa_Pabellon.py",
                "Piscina Estepa": "pages/Estepa_Piscina.py",
                "Campo de Fútbol Estepa": "pages/campofutbol_estepa.py"
            },
            # Agrega otros roles y sus páginas correspondientes aquí
        }

        # Obtener el rol del usuario actual
        user_role = user_roles.get(ss.username)

        # Agregar páginas según el rol del usuario
        if user_role in role_pages:
            pages.update(role_pages[user_role])

    # Crear el menú de navegación en la barra lateral
    selection = st.sidebar.selectbox("Seleccione una página", list(pages.keys()))
    page = pages[selection]

    # Ejecutar el script de la página seleccionada
    with open(page) as f:
        code = compile(f.read(), page, 'exec')
        exec(code, globals())
       