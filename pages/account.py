import streamlit as st
from streamlit import session_state as ss
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from modules.nav import MenuButtons

st.set_page_config(page_title="Centro de Control Iaxxon Energía", page_icon="https://i.imgur.com/JEX19oy.png", layout="wide")



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
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

authenticator.login(location='main')

if ss["authentication_status"]:
    authenticator.logout(location='sidebar')    
    st.write(f'Bienvenid@ *{ss["name"]}*')

elif ss["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif ss["authentication_status"] is None:
    st.warning('Please enter your username and password')

if st.session_state["authentication_status"]:
    try:
        if authenticator.reset_password(st.session_state["username"]):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)

with open('config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)   



# Call this late because we show the page navigator depending on who logged in.
MenuButtons(get_roles())