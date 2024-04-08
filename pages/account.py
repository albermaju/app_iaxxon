import streamlit as st
from streamlit import session_state as ss
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from modules.nav import MenuButtons


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


st.header('Account page')


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

login_tab, register_tab = st.tabs(['Login', 'Register'])

with login_tab:
    authenticator.login(location='main')

    if ss["authentication_status"]:
        authenticator.logout(location='main')    
        st.write(f'Welcome *{ss["name"]}*')

    elif ss["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif ss["authentication_status"] is None:
        st.warning('Please enter your username and password')

# Call this late because we show the page navigator depending on who logged in.
MenuButtons(get_roles())