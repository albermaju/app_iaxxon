import streamlit as st
from modules.nav import MenuButtons
from Centro_de_Control_Iaxxon_Energía import show_page as Iaxxon_Energia_show_page

def main():
    # Lógica de autenticación o configuración inicial si es necesario
    MenuButtons()  # Llamar al menú de navegación

if __name__ == "__main__":
    main()
