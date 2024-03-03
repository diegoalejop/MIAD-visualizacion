import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from ETL import df

# Título del dashboard
st.title("Dasboard Frescura en el Mercado")

# Muestra un mensaje
st.write("Datos del mercado de Abril 2021 - Diciembre 2023")


# Sidebar
ciudad_unico = df["Ciudad"].unique()
año_unico = df["año_produccion"].unique()
marca_unico = df["Marca"].unique()
canal_unico = df["Canal"].unique()

## Ordena las opciones si es necesario
ciudad_select = st.sidebar.multiselect('Selecciona una o más ciudades:', ciudad_unico)
ciudad_unico.sort()
año_unico.sort()
marca_unico.sort()
canal_unico.sort()

## objeto sidebar
año_select = st.sidebar.selectbox('Selecciona un año de producción:', año_unico)
marca_select = st.sidebar.selectbox('Selecciona una marca:', marca_unico)
canal_select = st.sidebar.multiselect('Selecciona uno o más canales:', canal_unico)

# Filtra el dataframe basado en las selecciones
filtered_df = df[(df['Ciudad'].isin(ciudad_select)) &
                 (df['año_produccion'] == año_select) & 
                 (df['Marca'].isin([marca_select])) & 
                 (df['Canal'].isin(canal_select))]


# Contenido

# Mostrar el dataframe filtrado o realizar otras operaciones con él
df_describe = filtered_df[["Edad_producto"]].describe().round(1)

# Filtrar el dataframe para frescura 'Inaceptable'
df_inaceptable = filtered_df[filtered_df['Frescura'] == 'Inaceptable']

# Contar la frecuencia de cada canal y obtener los top 10
conteo_canales = df_inaceptable['Canal'].value_counts().head(10)

# Convertir la serie de conteo_canales en un dataframe para Plotly
df_conteo_canales = conteo_canales.reset_index()
df_conteo_canales.columns = ['Canal', 'Cantidad']

df_describe_pivoted = df_describe.T
st.write(df_describe_pivoted)

# División para grafico de linea y pie
# Gráfico de lineas
fig_line = px.box(filtered_df, x='mes_encuesta', y='Edad_producto', title='Relación entre Fecha de Encuesta y Edad del Producto')
fig_line.update_layout(xaxis_title='Mes', yaxis_title='Edad del Producto')
fig_line.update_xaxes(range=[0.5, 12.5], dtick=1)
st.plotly_chart(fig_line)


col1, col2 = st.columns(2)

# with col1: 
    # st.write("Grafico cualquiera")
    # st.write(df) 

    
with col1:
    # Gráfico de pie
    conteo_frescura = filtered_df['Frescura'].value_counts()
    fig_pie = px.pie(names=conteo_frescura.index, values=conteo_frescura.values, title='Distribución de Frescura')
    fig_pie.update_layout(width=350, height=350)
    st.plotly_chart(fig_pie)
    
with col2:    
    # Crear el gráfico de barras para el top 10 de canales con frescura 'Inaceptable'
    # st.header("Top 10 Canales con Frescura Inaceptable")
    df_inaceptable = filtered_df[filtered_df['Frescura'] == 'Inaceptable']
    conteo_canales = df_inaceptable['Canal'].value_counts().head(10)
    df_conteo_canales = conteo_canales.reset_index()
    df_conteo_canales.columns = ['Canal', 'Cantidad']
    fig_bar = px.bar(
        df_conteo_canales,
        x='Canal',
        y='Cantidad',
        labels={'Canal': 'Canal', 'Cantidad': 'Cantidad'},
        title='Top 10 Canales con Frescura Inaceptable',
        color_discrete_sequence=['red']  # Esto cambiará el color de las barras a rojo
    )
    fig_bar.update_layout(width=350, height=350)
    st.plotly_chart(fig_bar)





    
