import streamlit as st
from streamlit import session_state as ss
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pages import Estepa_Pabellon, Estepa_Piscina, colegiodobrasil, bodegashabla, campofutbol_estepa, duplex, huetorvega_pabellon, pabellon_aguilar, piscina_pedrera, piscina_priego, Toyota_Hispaljarafe

st.set_page_config(page_title="Centro de Control Iaxxon Energía", page_icon="https://i.imgur.com/JEX19oy.png", layout="wide", initial_sidebar_state= "auto")


#######################################
# CONFIGURACIÓN DE PÁGINA
#######################################

# Custom HTML/CSS for the banner
custom_html = """
<div class="banner">
    <img src="https://i.imgur.com/SJQWq0F.png" alt="Banner Image">
</div>
<style>
    .banner {
	    margin: 30px auto;
	    width: 40%;
	    min-width: 230px;
	    max-width: 330px;
	    position: relative;
	    height: auto;
	    min-height: 300px;
	    max-height: 500px;
	    overflow: hidden;
    }
    .banner img {
	    max-width : 330px;
	    width: 100%;
	    position: absolute;
    }
</style>
"""
# Display the custom HTML
st.components.v1.html(custom_html)

CONFIG_FILENAME = 'config.yaml'
with open(CONFIG_FILENAME) as file:
    config = yaml.load(file, Loader=SafeLoader)


def get_roles():
    """Gets user roles based on config file."""
    with open(CONFIG_FILENAME) as file:
        config = yaml.load(file, Loader=SafeLoader)

    if config is not None:
        cred = config['credentials']
    else:
        cred = {}

    return {username: user_info['role'] for username, user_info in cred['usernames'].items() if 'role' in user_info}


st.header('Centro de control')


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

login_tab, resetpassword_tab = st.tabs(['Iniciar Sesión', 'Nueva Contraseña'])

with login_tab:
    authenticator.login(location='main')

    if ss["authentication_status"]:
        authenticator.logout(location='main')    
        st.write(f'Bienvenid@ *{ss["name"]}*')

    elif ss["authentication_status"] is False:
        st.error('Usuario o contraseña incorrectos')
    elif ss["authentication_status"] is None:
        st.warning('Por favor, introduzca tu usuario y contraseña')

with resetpassword_tab:
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"]):
                st.success('Contraseña modificada con éxito')
        except Exception as e:
            st.error(e)

with open('config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)      

# Call this late because we show the page navigator depending on who logged in.
# MenuButtons(get_roles())
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