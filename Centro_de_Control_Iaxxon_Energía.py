import streamlit as st

st.set_page_config(
    page_title="Centro de Control Iaxxon Energía",
    page_icon="https://i.imgur.com/JEX19oy.png",
)

st.write("# Bienvenido al Centro de Control de Iaxxon Energía! 👋")

st.sidebar.success("Seleciona la instalación a visualizar")

st.markdown(
    """
   Aquí podrás monitorizar toda tu instalación y analizar como ha operado en los diferentes rangos de tiempo.

    **👈 Selecciona tu instalación en el menú de la izquierda**

"""
)