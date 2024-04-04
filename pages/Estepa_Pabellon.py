import streamlit as st
import influxdb_client 
import pandas as pd
from pandas import DataFrame, Series, Timestamp
from pandas.errors import EmptyDataError
import duckdb
import yaml
from yaml.loader import SafeLoader
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

#######################################
# CONFIGURACIÓN DE PÁGINA
#######################################
st.set_page_config(page_title="Centro de Control Iaxxon | Piscina de Estepa", page_icon="https://i.imgur.com/JEX19oy.png", layout="wide")

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
st.title("Centro de Control")

#######################################
# INFLUXDB
#######################################
org = "a.marana@equsdesign.com"
bucket1 = "Estepa_Piscina_v3"
token = "OepRh4h6woJ_yFar3rxWTKhKW9ryBLMpcBLV7T5OE_3dsuJwTJv3rbZLUUkDI3ht1__Wedk_a0E4-126YtcK-g=="
url = "https://eastus-1.azure.cloud2.influxdata.com"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

#######################################
# CARGA DE DATOS
#######################################

def get_data(time_period):

    # Obtener la fecha actual
    end_time = datetime.utcnow()

    if time_period == '1 día':
        start_time = '1d'
    elif time_period == '2 días':
        start_time = '2d'
    elif time_period == '7 días':
        start_time = '7d'
    elif time_period == '1 mes':
        start_time = '30d'

    # Formatear las fechas en el formato aceptado por InfluxDB


    # Construir la consulta   
    query_api = client.query_api()
    query= f'from (bucket: "Estepa_Piscina_v3")\
    |> range(start: -{start_time})\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    result = query_api.query_data_frame(org=org, query=query.strip())
    return result

# Lista de opciones para el desplegable
options = ['1 día', '2 días', '7 días', '1 mes']

# Desplegable para seleccionar el período de tiempo
time_period = st.selectbox('Selecciona el período de tiempo:', options)
df = get_data(time_period)

to_drop = ['result', 'table', '_measurement', 'tag1', 'tag2']
df.drop(to_drop, inplace=True, axis=1)
df['TCAP']=df['TCAP'].round(2)
df['TDAC']=df['TDAC'].round(2)
df['TINT']=df['TINT'].round(2)
df.rename(columns = {'_time':'Tiempo'}, inplace = True) 

with st.expander("Previsualización de datos"):
    st.dataframe(df)


#######################################
# DISEÑO PÁGINA STREAMLIT
#######################################


st.title("Estado Actual")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Temperatura Captador (ºC)", value=df.TCAP.iloc[-1])
    st.metric(label="Energía Producida (kWh)", value=df.TDAC.iloc[-1])

with col2:
    st.metric(label="Temperatura Intercambiador (ºC)", value=df.TINT.iloc[-1])
    st.toggle('Bomba')

with col3:
    st.metric(label="Temperatura Depósito (ºC)", value=df.TDAC.iloc[-1])
    st.toggle('Ventilador')


st.title("Gráficas")
with st.container():
    fig = px.line(df, x="Tiempo", y="TCAP",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Captador')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit")

with st.container():
    fig = px.line(df, x="Tiempo", y="TDAC",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Depósito Caliente')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit")

with st.container():
    fig = px.line(df, x="Tiempo", y="TINT",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Intercambiador')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit")

with st.container():
    fig = px.line(df, x="Tiempo", y="TDAF",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Depósito Agua Fría')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit")
    
