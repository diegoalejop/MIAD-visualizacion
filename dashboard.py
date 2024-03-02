import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from ETL import df

# Título del dashboard
st.title("Dasboard Frescura en el Mercado")

# Muestra un mensaje
st.write("Datos del mercado de Abril 2021 - Diciembre 2023")
#------------------------------------------------------------------------------------------
# Sidebar
año_unico = df["año_produccion"].unique()
marca_unico = df["Marca"].unique()
canal_unico = df["Canal"].unique()

## Ordena las opciones si es necesario
año_unico.sort()
marca_unico.sort()
canal_unico.sort()

## objeto sidebar
año_select = st.sidebar.selectbox('Selecciona un año de producción:', año_unico)
marca_select = st.sidebar.selectbox('Selecciona una marca:', marca_unico)
canal_select = st.sidebar.multiselect('Selecciona uno o más canales:', canal_unico)

# ----------------------------------------------------------------------------------------
# Filtra el dataframe basado en las selecciones
filtered_df = df[(df['año_produccion'] == año_select) & 
                 (df['Marca'].isin([marca_select])) & 
                 (df['Canal'].isin(canal_select))]
#------------------------------------------------------------------------------------------
# Contenido


# Mostrar el dataframe filtrado o realizar otras operaciones con él
st.write(filtered_df[["Edad_producto"]].describe())

## Gráfico de lineas
fig = px.box(filtered_df, x='mes_encuesta', y='Edad_producto', title='Relación entre Fecha de Encuesta y Edad del Producto')

# Añadir títulos a los ejes (opcional)
fig.update_layout(xaxis_title='Mes', yaxis_title='Edad del Producto')
fig.update_xaxes(range=[0, 12], dtick=1)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)
