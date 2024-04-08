import streamlit as st
from streamlit_extras.app_logo import add_logo
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
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
authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status:
    authenticator.logout('Logout', 'main')
    if username == 'jsmith':
        st.write(f'Welcome *{name}*')
        st.title('Application 1')
    elif username == 'rbriggs':
        st.write(f'Welcome *{name}*')
        st.title('Application 2')
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')