import streamlit as st
from streamlit_extras.app_logo import add_logo
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities.exceptions import (CredentialsError,
                                                          ForgotError,
                                                          LoginError,
                                                          RegisterError,
                                                          ResetError,
                                                          UpdateError) 
from menu import menu


with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

st.set_page_config(
    page_title="Centro de Control Iaxxon Energía",
    page_icon="https://i.imgur.com/JEX19oy.png",
)

st.write("# Bienvenido al Centro de Control de Iaxxon Energía! 👋")

st.sidebar.success("Seleciona la instalación a visualizar")

st.markdown(
    """
   Aquí podrás monitorizar toda tu instalación y analizar como ha operado en los diferentes rangos de tiempo.

    **Inicia sesión con tus credenciales:**

"""
)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Creating a login widget
try:
    name, authentication_status, username = authenticator.login('main')
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    st.session_state.authentication_status = True
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
elif st.session_state["authentication_status"] is False:
    st.session_state.authentication_status = False
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.session_state.authentication_status = None
    st.warning('Please enter your username and password')

# Creating a password reset widget
if st.session_state["authentication_status"]:
    try:
        if authenticator.reset_password(st.session_state["username"]):
            st.success('Password modified successfully')
    except ResetError as e:
        st.error(e)
    except CredentialsError as e:
        st.error(e)

# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)