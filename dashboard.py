import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
# from modules.ETL import df

datos = pd.read_excel("Datos.xlsx", sheet_name='Export')

## Transformación de datos

# Obtener columna Fecha_produccion: Fecha_vencimiento  - Vida_util
datos['Vida_util_timedelta'] = pd.to_timedelta(datos['Vida_util'], unit='D')
datos['Fecha_produccion'] = datos['Fecha_vencimiento'] - datos['Vida_util_timedelta']

# Split por espacio de la columna Referencia para obtener Marca, Empaque, Volumen, Und_volumen, Retornable y Texto
datos[['Marca', 'Empaque', 'Volumen', 'Und_Volumen', 'Retornable','Texto']] = datos['Referencia'].str.split(expand=True)

# Cambiar Retornable por Si
datos['Retornable'] = datos['Retornable'].replace('Retornable', 'SI')

# Creación de columnas año_produccion y mes_produccion, a partir de Fecha_produccion
datos['año_produccion'] = datos['Fecha_produccion'].dt.year
datos['mes_produccion'] = datos['Fecha_produccion'].dt.month

# Creación de columnas año_encuesta y mes_encuesta, a partir de Fecha_encuesta
datos['año_encuesta'] = datos['Fecha_encuesta'].dt.year
datos['mes_encuesta'] = datos['Fecha_encuesta'].dt.month

# Eliminación de columnas innecesarias para la visualización
datos = datos.drop(columns=['Referencia', 'Establecimiento', 'Lote', 'Vida_util_timedelta', 'Texto', 'Und_Volumen', 'Fecha_vencimiento'])

# Cálculo de la columna frescura teniendo en cuenta sus respectivas condiciones
def calculo_frescura(row):
    # Condiciones Marca_1, Marca_2, Marca_3
    if row['Marca'] in ['Marca_1', 'Marca_2', 'Marca_3']:
        if row['Edad_producto'] < 90:
            return 'Ideal'
        elif 90 < row['Edad_producto'] <= 120:
            return 'Debe Mejorar'
        else:
            return 'Inaceptable'
    # Condiciones Marca_4, Marca_5, Marca_6, Marca_7
    elif row['Marca'] in ['Marca_4', 'Marca_5', 'Marca_6', 'Marca_7']:
        if row['Edad_producto'] < 60:
            return 'Ideal'
        elif 60 < row['Edad_producto'] <= 100:
            return 'Debe Mejorar'
        else:
            return 'Inaceptable'

# Aplicar la función para crear la nueva columna
datos['Frescura'] = datos.apply(calculo_frescura, axis=1)

# Crear columnas con límite "Debe Mejorar" e "Inaceptable" para cada Marca

datos['Lim_debe_mejorar'] = pd.NA
datos['Lim_inaceptable'] = pd.NA

datos.loc[datos['Marca'].isin(['Marca_1', 'Marca_2', 'Marca_3']), 'Lim_debe_mejorar'] = 90
datos.loc[datos['Marca'].isin(['Marca_1', 'Marca_2', 'Marca_3']), 'Lim_inaceptable'] = 120

datos.loc[datos['Marca'].isin(['Marca_4', 'Marca_5', 'Marca_6', 'Marca_7']), 'Lim_debe_mejorar'] = 60
datos.loc[datos['Marca'].isin(['Marca_4', 'Marca_5', 'Marca_6', 'Marca_7']), 'Lim_inaceptable'] = 100

df = datos

# Título del dashboard
st.title('Dasboard Frescura en el Mercado')

# Muestra un mensaje
st.write('Datos del mercado de Abril 2021 - Diciembre 2023')


# Sidebar
ciudad_unico = df['Ciudad'].unique()
año_unico = df['año_produccion'].unique()
marca_unico = df['Marca'].unique()
canal_unico = df['Canal'].unique()

## Ordena las opciones si es necesario
ciudad_unico.sort()
año_unico.sort()
marca_unico.sort()
canal_unico.sort()

## objeto sidebar
ciudad_select = st.sidebar.multiselect('Selecciona una o más ciudades:', ciudad_unico)
año_select = st.sidebar.selectbox('Selecciona un año de producción:', año_unico)
marca_select = st.sidebar.selectbox('Selecciona una marca:', marca_unico)
canal_select = st.sidebar.multiselect('Selecciona uno o más canales:', canal_unico)

if not canal_select or ciudad_select:  # Si no se seleccionó ningún canal o ciudad, mostrar datos para todos los canales y ciudades
    filtered_df = df[(df['año_produccion'] == año_select) & 
                     (df['Marca'].isin([marca_select]))]
else:
    filtered_df = df[(df['año_produccion'] == año_select) & 
                     (df['Marca'].isin([marca_select])) & 
                     (df['Canal'].isin(canal_select)) & 
                     (df['Ciudad'].isin(canal_select))]
    

# Contenido
# Mostrar el dataframe filtrado o realizar otras operaciones con él
df_describe = filtered_df[['Edad_producto']].describe().round(1)

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

# Gráfico de cajas
# --------------------------------------------------------
fig_box = px.box(filtered_df, x='mes_encuesta', y='Edad_producto', title='Tendencia de la Edad del Producto')
fig_box.update_layout(xaxis_title='Mes', yaxis_title='Edad del Producto')
fig_box.update_xaxes(range=[0.5, 12.5], dtick=1)
st.plotly_chart(fig_box)

# Gráfico de caja por empaque
# --------------------------------------------------------
fig_box = px.box(filtered_df, 
                 x='mes_encuesta', 
                 y='Edad_producto',
                 color= 'Empaque',
                 title='Relación entre Empaque y Edad del Producto')
fig_box.update_layout(xaxis_title='Mes', yaxis_title='Edad del Producto')
fig_box.update_xaxes(range=[0.5, 12.5], dtick=1)
st.plotly_chart(fig_box)

# Gráfico de linea por ciudad
# --------------------------------------------------------
df_grp_ret = filtered_df.groupby(['mes_encuesta', 'Ciudad'])['Edad_producto'].mean().reset_index()
fig_line_ret = px.line(df_grp_ret, x='mes_encuesta', y='Edad_producto', color='Ciudad', 
              title='Promedio Mensual de Frescura por Ciudad',
              labels={'Mes': 'Mes', 'Frescura': 'Frescura'})
fig_line_ret.update_xaxes(range=[0.5, 12.5], dtick=1)
st.plotly_chart(fig_line_ret)

# Gráfico de linea por retornabilidad
# --------------------------------------------------------
df_grp_ret = filtered_df.groupby(['mes_encuesta', 'Retornable'])['Edad_producto'].mean().reset_index()
fig_line_ret = px.line(df_grp_ret, x='mes_encuesta', y='Edad_producto', color='Retornable', 
              title='Promedio Mensual de Frescura por Retornabilidad',
              labels={'Mes': 'Mes', 'Frescura': 'Frescura'})
fig_line_ret.update_xaxes(range=[0.5, 12.5], dtick=1)
st.plotly_chart(fig_line_ret)


# División en columnas
# --------------------------------------------------------
col1, col2 = st.columns(2)

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





    
