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
city="Granada"
unit="Celsius"
speed="Kilometre/hour"
temp_unit=" °C"
wind_unit=" km/h"

api="9b833c0ea6426b70902aa7a4b1da285c"
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
    st.subheader("Pabellón de Huétor Vega")
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

def get_data(time_period):

    # Obtener la fecha actual
    end_time = datetime.utcnow()

    if time_period == '1 hora':
        start_time = '1h'
    if time_period == '1 día':
        start_time = '1d'
    elif time_period == '2 días':
        start_time = '2d'
    elif time_period == '7 días':
        start_time = '7d'
    elif time_period == '1 mes':
        start_time = '30d'
    elif time_period == '1 año':
        start_time = '365d'

    # Formatear las fechas en el formato aceptado por InfluxDB


    # Construir la consulta   
    query_api = client.query_api()
    query= f'from (bucket: "Estepa_Piscina_v3")\
    |> range(start: -{start_time})\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    result = query_api.query_data_frame(org=st.secrets.db_credentials.org, query=query.strip())
    return result

def get_kwh(time_period):

    # Obtener la fecha actual
    end_time = datetime.utcnow()

    if time_period == '1 hora':
        start_time = '1h'
    if time_period == '1 día':
        start_time = '1d'
    elif time_period == '2 días':
        start_time = '2d'
    elif time_period == '7 días':
        start_time = '7d'
    elif time_period == '1 mes':
        start_time = '31d'
    elif time_period == '1 año':
        start_time = '1y'

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

    result = query_api.query_data_frame(org=st.secrets.db_credentials.org, query=query)
    return result

query_api = client.query_api()
query_fan = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: -24h)\
    |> filter(fn: (r) => r["_field"] == "fan")\
    |> aggregateWindow(every: 1m, fn: last, createEmpty: false)\
    |> yield(name: "last")'''

query_pump = f'''from(bucket: "Estepa_Piscina_v3")\
    |> range(start: -24h)\
    |> filter(fn: (r) => r["_field"] == "pump")\
    |> aggregateWindow(every: 1m, fn: last, createEmpty: false)\
    |> yield(name: "last")'''
    
dffan = query_api.query_data_frame(org=st.secrets.db_credentials.org, query=query_fan)
estado_ventilador = dffan["_value"].iloc[-1]  # Tomamos el último valor de la serie de tiempo

dfpump = query_api.query_data_frame(org=st.secrets.db_credentials.org, query=query_pump)
estado_bomba = dfpump["_value"].iloc[-1]  # Tomamos el último valor de la serie de tiempo


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