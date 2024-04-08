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
from streamlit_extras.altex import _chart 
import streamlit_toggle as tog
from streamlit import session_state as ss
from modules.nav import MenuButtons
from pages.account import get_roles


st.set_page_config(page_title="Centro de Control Iaxxon | Piscina de Estepa", page_icon="https://i.imgur.com/JEX19oy.png", layout="wide")

if 'authentication_status' not in ss:
    st.switch_page('./pages/account.py')

MenuButtons(get_roles())

if ss["authentication_status"]:
    authenticator.logout(location='main')    
    st.write(f'Bienvenid@ *{ss["name"]}*')


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
st.title("Centro de Control | Piscina de Estepa")

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

def get_kwh(time_period):

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
    query = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: -{start_time})\
    |> filter(fn: (r) => r["_measurement"] == "prueba")\
    |> filter(fn: (r) => r["_field"] == "TINT" or r["_field"] == "pump" or r["_field"] == "TDAF")\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
    |> map(fn: (r) => ({{_start: r._start,_stop: r._stop,result: r.result,_time: r._time,_measurement: r._measurement,_field: "energia_kwh",_value: (float(v: r.TINT) - float(v: r.TDAF)) * float(v: r.pump) * 0.046}}),)\
    |> filter(fn: (r) => r["_field"] == "energia_kwh")\
    |> sum()'''

    result = query_api.query_data_frame(org="my-org", query=query)
    return result

query_api = client.query_api()
query_fan = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: -30m)\
    |> filter(fn: (r) => r["_field"] == "fan")\
    |> aggregateWindow(every: 1m, fn: last, createEmpty: false)\
    |> yield(name: "last")'''

query_pump = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: -30m)\
    |> filter(fn: (r) => r["_field"] == "pump")\
    |> aggregateWindow(every: 1m, fn: last, createEmpty: false)\
    |> yield(name: "last")'''
    
dffan = query_api.query_data_frame(org="my-org", query=query_fan)
estado_ventilador = dffan["_value"].iloc[-1]  # Tomamos el último valor de la serie de tiempo

dfpump = query_api.query_data_frame(org="my-org", query=query_pump)
estado_bomba = dfpump["_value"].iloc[-1]  # Tomamos el último valor de la serie de tiempo

# Lista de opciones para el desplegable
options = ['1 día', '2 días', '7 días', '1 mes']

# Desplegable para seleccionar el período de tiempo
time_period = st.selectbox('Selecciona el período de tiempo:', options)
df = get_data(time_period)
df2 = get_kwh(time_period)

to_drop = ['result', 'table', '_measurement', 'tag1', 'tag2']
df.drop(to_drop, inplace=True, axis=1)
df['TCAP']=df['TCAP'].round(2)
df['TDAC']=df['TDAC'].round(2)
df['TINT']=df['TINT'].round(2)
df2['_value']=df2['_value'].round(2)
df.rename(columns = {'_time':'Tiempo'}, inplace = True) 

#######################################
# DISEÑO PÁGINA STREAMLIT
#######################################

st.title("Estado Actual")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Temperatura Captador", value=f"{df.TCAP.iloc[-1]} °C")
    st.metric(label="Energía Producida", value=f"{df2._value.iloc[-1]} kWh")

with col2:
    st.metric(label="Temperatura Intercambiador", value=f"{df.TINT.iloc[-1]} °C")
    st.metric(label="Temperatura Depósito", value=f"{df.TDAC.iloc[-1]} °C")

with col3:
    st.markdown("")
    tog.st_toggle_switch(
        label="Bomba ",
        key="switch_1",
        default_value= estado_bomba,
        label_after=True,
        inactive_color="#D3D3D3",
        active_color="#D3D3D3", 
        track_color="#008f39", 
    )
    st.markdown("") 
    tog.st_toggle_switch(
        label="Ventilador ",
        key="switch_2",
        default_value= estado_ventilador,
        label_after=True,
        inactive_color="#D3D3D3",  # optional
        active_color="#D3D3D3",  # optional
        track_color="#008f39",  # optional
    )

st.title("Gráficas")
config = {'displayModeBar': False}
st.markdown(
    """
    <style>
    .css-17y5rwz {
        overflow-x: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
with st.container():
    fig = px.line(df, x="Tiempo", y="TCAP",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Captador')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit", config=config)

with st.container():
    fig = px.line(df, x="Tiempo", y="TDAC",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Depósito Caliente')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit", config=config)

with st.container():
    fig = px.line(df, x="Tiempo", y="TINT",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Intercambiador')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit", config=config)

with st.container():
    fig = px.line(df, x="Tiempo", y="TDAF",
                  hover_data={"Tiempo": "|%H:%M,  %d/%m"},
                  title='Temperatura Depósito Agua Fría')
    st.plotly_chart(fig, use_container_width=True,theme="streamlit", config=config)
    