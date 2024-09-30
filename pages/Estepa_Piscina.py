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
import requests
import datetime
from datetime import datetime, timedelta
from streamlit_extras.altex import _chart 
import streamlit_toggle as tog
from streamlit import session_state as ss
from modules.nav import MenuButtons
from pages.account import get_roles
import streamlit_authenticator as stauth


st.set_page_config(layout="wide")

if 'authentication_status' not in ss:
    st.switch_page('./pages/account.py')

MenuButtons(get_roles())

#######################################
# API TIEMPO
#######################################
city="Estepa"
unit="Celsius"
speed="Kilometre/hour"
temp_unit=" °C"
wind_unit=" km/h"

api="ad580a816236d62b1dde3cc3ba900651"
url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}"
response=requests.get(url)
x=response.json()

try:
    lon=x["coord"]["lon"]
    lat=x["coord"]["lat"]
    ex="current,minutely,hourly"
    url2=f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={ex}&lang=sp&appid={api}'
    res=requests.get(url2)
    y=res.json()

    maxtemp=[]
    mintemp=[]
    pres=[]
    humd=[]
    wspeed=[]
    desc=[]
    cloud=[]
    rain=[]
    dates=[]
    sunrise=[]
    sunset=[]
    cel=273.15
            
    for item in y["daily"]:
        if unit=="Celsius":
            maxtemp.append(round(item["temp"]["max"]-cel,2))
            mintemp.append(round(item["temp"]["min"]-cel,2))
        else:
            maxtemp.append(round((((item["temp"]["max"]-cel)*1.8)+32),2))
            mintemp.append(round((((item["temp"]["min"]-cel)*1.8)+32),2))

        if wind_unit=="m/s":
            wspeed.append(str(round(item["wind_speed"],1))+wind_unit)
        else:
            wspeed.append(str(round(item["wind_speed"]*3.6,1))+wind_unit)

        pres.append(item["pressure"])
        humd.append(str(item["humidity"])+' %')
                
        cloud.append(str(item["clouds"])+' %')
        rain.append(str(int(item["pop"]*100))+'%')

        desc.append(item["weather"][0]["description"].title())

    def bargraph():
        fig=go.Figure(data=
            [
            go.Bar(name="Maximum",x=dates,y=maxtemp,marker_color='crimson'),
            go.Bar(name="Minimum",x=dates,y=mintemp,marker_color='navy')
            ])
        fig.update_layout(xaxis_title="Dates",yaxis_title="Temperature",barmode='group',margin=dict(l=70, r=10, t=80, b=80),font=dict(color="white"))
        st.plotly_chart(fig)
            
    def linegraph():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=mintemp, name='Minimum '))
        fig.add_trace(go.Scatter(x=dates, y=maxtemp, name='Maximimum ',marker_color='crimson'))
        fig.update_layout(xaxis_title="Dates",yaxis_title="Temperature",font=dict(color="white"))
        st.plotly_chart(fig)
                
    icon=x["weather"][0]["icon"]
    current_weather=x["weather"][0]["description"].title()
            
    if unit=="Celsius":
        temp=str(round(x["main"]["temp"]-cel,2))
    else:
        temp=str(round((((x["main"]["temp"]-cel)*1.8)+32),2))

    url_png = f'http://openweathermap.org/img/w/{icon}.png'

except KeyError:
    st.error("¡Ciudad no encontrada!")

#######################################
# CONFIGURACIÓN DE PÁGINA
#######################################
col1, col2, col3 = st.columns(3)

with col1:
    # Custom HTML/CSS for the banner
    custom_html = """
    <div class="banner">
        <img src="https://i.imgur.com/SJQWq0F.png" alt="Banner Image">
    </div>
    <style>
    .banner {
	    margin: 0px;
        margin-bottom: 20px;
	    width: 100%;
	    min-width: 110px;
	    max-width: 140px;
	    position: relative;
	    height: auto;
	    min-height: 40px;
	    max-height: 100px;
	    overflow: hidden;
    }
    .banner img {
	    max-width : 140px;
	    max-width : 140px;
	    width: 100%;
	    position: absolute;
    }
    </style>
    """

    # Display the custom HTML
    st.markdown(custom_html, unsafe_allow_html=True)
    # Lista de opciones para el desplegable
    options = ['1 hora', '1 día', '2 días', '7 días', '1 mes', '1 año']

    # Desplegable para seleccionar el período de tiempo
    time_period = st.selectbox('Selecciona el período de tiempo:', options)

with col2:
    st.subheader("Piscina Estepa")
    st.metric(f"Clima en {city}",temp+temp_unit)

with col3:
    st.subheader("Estado Actual")
    st.image(url_png, width=80)
    st.subheader(" ")
        
#######################################
# INFLUXDB
#######################################

client = influxdb_client.InfluxDBClient(
    url=st.secrets.db_credentials.url,
    token=st.secrets.db_credentials.token,
    org=st.secrets.db_credentials.org
    )

#######################################
# CARGA DE DATOS
#######################################

# Fecha de finalización (1 de julio de 2024 a las 00:00 UTC)
end_time = datetime(2024, 7, 1, 0, 0, 0)

# Función para calcular start_date en función del período seleccionado
def calculate_start_date(time_period):
    if time_period == '1 hora':
        delta = timedelta(hours=1)
    elif time_period == '1 día':
        delta = timedelta(days=1)
    elif time_period == '2 días':
        delta = timedelta(days=2)
    elif time_period == '7 días':
        delta = timedelta(weeks=1)
    elif time_period == '1 mes':
        delta = timedelta(days=31)  # Aproximado a un mes
    elif time_period == '1 año':
        delta = timedelta(days=365)  # Aproximado a un año
    else:
        raise ValueError("Período de tiempo no soportado.")

    # Calcular el start_date restando el delta del end_time
    start_time = end_time - delta

    # Convertir las fechas a formato ISO 8601 para InfluxDB
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    return start_time_str, end_time_str

# Función para obtener datos según el período de tiempo seleccionado
def get_data(time_period):
    # Obtener las fechas de inicio y fin en función del período seleccionado
    start_time_str, end_time_str = calculate_start_date(time_period)

    # Construir la consulta con el rango dinámico de fechas
    query_api = client.query_api()
    query = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: {start_time_str}, stop: {end_time_str})\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'''

    result = query_api.query_data_frame(org=st.secrets.db_credentials.org, query=query.strip())
    return result

# Función para calcular el KWh en función del período de tiempo
def get_kwh(time_period):
    # Obtener las fechas de inicio y fin en función del período seleccionado
    start_time_str, end_time_str = calculate_start_date(time_period)

    # Construir la consulta con el rango dinámico de fechas
    query_api = client.query_api()
    query = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: {start_time_str}, stop: {end_time_str})\
    |> filter(fn: (r) => r["_measurement"] == "prueba")\
    |> filter(fn: (r) => r["_field"] == "TINT" or r["_field"] == "pump" or r["_field"] == "TDAF")\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
    |> map(fn: (r) => ({{_start: r._start,_stop: r._stop,result: r.result,_time: r._time,_measurement: r._measurement,_field: "energia_kwh",_value: (float(v: r.TINT) - float(v: r.TDAF)) * float(v: r.pump) * 0.046}}),)\
    |> filter(fn: (r) => r["_field"] == "energia_kwh")\
    |> sum()'''

    result = query_api.query_data_frame(org=st.secrets.db_credentials.org, query=query)
    return result

# Ejecución de consultas de ventilador y bomba
query_api = client.query_api()
query_fan = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: 2024-07-01T12:00:00Z, stop: 2024-07-01T13:00:00Z)\
    |> filter(fn: (r) => r["_field"] == "fan")\
    |> aggregateWindow(every: 1m, fn: last, createEmpty: false)\
    |> yield(name: "last")'''

query_pump = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: 2024-07-01T12:00:00Z, stop: 2024-07-01T13:00:00Z)\
    |> filter(fn: (r) => r["_field"] == "pump")\
    |> aggregateWindow(every: 1m, fn: last, createEmpty: false)\
    |> yield(name: "last")'''

to_drop = ['result', 'table', '_measurement']

# Obtener los datos del ventilador
dffan = query_api.query_data_frame(org=st.secrets.db_credentials.org, query=query_fan)
if not isinstance(dffan, list):
    dffan = [dffan]
dffan = pd.concat(dffan, ignore_index=True)
dffan.drop(to_drop, inplace=True, axis=1)

# Obtener los datos según el período seleccionado
time_period = '7 días'  # Cambia esto a cualquier otro valor que quieras
df = get_data(time_period)
if not isinstance(df, list):
    df = [df]

df = pd.concat(df, ignore_index=True)
df.drop(to_drop, inplace=True, axis=1)
df.sort_values(by='_time', ascending=True, inplace=True)

# Obtener el estado del ventilador y bomba
estado_ventilador = dffan['_value'].iloc[-1]  # Último valor de la serie temporal del ventilador
dfpump = query_api.query_data_frame(org=st.secrets.db_credentials.org, query=query_pump)
if not isinstance(dfpump, list):
    dfpump = [dfpump]
dfpump = pd.concat(dfpump, ignore_index=True)
dfpump.drop(to_drop, inplace=True, axis=1)

estado_bomba = dfpump['_value'].iloc[-1]  # Último valor de la serie temporal de la bomba

# Calcular KWh
df2 = get_kwh(time_period)

df['TCAP']=df['TCAP'].round(2)
df['TDAC']=df['TDAC'].round(2)
df['TINT']=df['TINT'].round(2)
df2['_value']=df2['_value'].round(2)
df.rename(columns = {'_time':'Tiempo'}, inplace = True) 

#######################################
# DISEÑO PÁGINA STREAMLIT
#######################################



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

st.subheader("Gráficas")
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

st.markdown('''
    <style>
    button[title="View fullscreen"] {
    background-color: #004170cc;
    right: 0;
    color: white;
    }

    button[title="View fullscreen"]:hover {
        background-color:  #004170;
        color: white;
        }
    </styles>
    ''', 
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
    