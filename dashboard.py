import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import time

# Inyectar CSS para cambiar el color de fondo utilizando st.markdown
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');

    .stApp {
        background-color: #e0e0e0;
    }

    /* Aumentar la especificidad para los elementos de texto dentro de st.info */
    .stAlert>div>div {
        font-family: 'Open Sans', sans-serif !important;
        font-size: 15px !important; /* Asegúrate de que el tamaño de la fuente se aplique */    
        color: #000000 !important; /* Asegura que el color se aplique */
    }
    </style>
    """, unsafe_allow_html=True)


datos = pd.read_excel("Datos.xlsx", sheet_name='Export')

# Define un mapa de colores para 'Frescura' usando códigos hexadecimales
color_discrete_map = {
    'Ideal': '#E2E062',  
    'Debe Mejorar': '#73AC61',  
    'Inaceptable': '#297159'  
}

# Especifica el orden de las categorías para 'Frescura'
category_orders = {
    'Frescura': ['Ideal', 'Debe Mejorar', 'Inaceptable']
}

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

####Hoja de descripción

# Título del dashboard
st.title('¿Qué tan fresco es lo que consumes?')

# Fecha de datos
st.write('Datos del mercado de Abril 2021 - Diciembre 2023')

#Descripción del dashboard
st.write("La medida de frescura de las bebidas distribuidas al por mayor" 
         "es clave para evaluar la calidad de los productos en el mercado,"
          "su popularidad y su futura producción. Diferentes condiciones y situaciones influyen esta medida,"
           "por lo que conocerlas puede ser beneficioso para tu siguiente compra.")

#Descripción de frescura
st.header('¿Cómo se mide la frescura?')
st.write("La frescura se evalúa a través del tiempo en días que lleva el producto en el mercado desde su "
         "producción. Productos que lleven mucho tiempo en las repisas se consideran menos frescos, por lo "
         "que suelen tener una calidad más baja. Algunos llegan a tener calidades inaceptables al llevar mucho "
         "tiempo sin ser consumidos.")


desc_Edad1 = """
    La cantidad de días que lleva el producto en el mercado también se puede interpretar como la edad del producto. 
    Esta misma edad, puede clasificarse en tres categorías que determinan si la frescura es idónea:
"""

desc_Edad2 = """
    Como consumidor una edad elevada de producto, es equivalente a una frescura baja y por ende una calidad subóptima.
"""

def stream_data():
    for word in desc_Edad1.split(" "):
        yield word + " "
        time.sleep(0.02)

    yield pd.DataFrame(datos['Frescura'].drop_duplicates())

    for word in desc_Edad2.split(" "):
        yield word + " "
        time.sleep(0.02)

if st.button("Edad de producto"):
    st.write_stream(stream_data)

#########
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
# --------------------------------------------------------
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

# Descripción del dasboard
st.info(
    "Este dashboard esta diseñado para ofrecer un visión clara y detallada "
    "de la frescura de nuestros productos a lo largo del tiempo, en diferentes "
    "ciudades, canales y tipos de empaque. ")

st.write(df_describe_pivoted)

# División para grafico de linea y pie

# Gráfico de cajas
# --------------------------------------------------------
fig_box = px.box(filtered_df, x='mes_encuesta', y='Edad_producto', title='Tendencia de la Edad del Producto')
fig_box.update_layout(xaxis_title='Mes', yaxis_title='Edad del Producto')
fig_box.update_xaxes(range=[0.5, 12.5], dtick=1)
# Actualiza el color de las cajas
fig_box.update_traces(marker_color='#E2E062', line_color='#73AC61')

fig_box.update_layout(
    title=dict(
        text='Tendencia de la Edad del Producto',
        font=dict(
            family="Roboto",  # Aplica la fuente Roboto
            size=20,  # Tamaño de la fuente
            color='black'  # Color de la fuente
        )
    ),
)

st.plotly_chart(fig_box)

st.info(
    "Descripción grafico por Edad Producto. ")

st.warning("¡ Menores valores de frescura" 
           "significan una mejor calidad del producto al consumidor !")

# Gráfico de caja por empaque
# --------------------------------------------------------
color_discrete_map_2 = {'Lata': '#E2E062', 'Botella': '#73AC61'}

fig_box = px.box(filtered_df, 
                 x='mes_encuesta', 
                 y='Edad_producto',
                 color= 'Empaque',
                 title='Relación entre Empaque y Edad del Producto',
                 color_discrete_map=color_discrete_map_2)
                 
fig_box.update_layout(xaxis_title='Mes', yaxis_title='Edad del Producto')
fig_box.update_xaxes(range=[0.5, 12.5], dtick=1)

fig_box.update_layout(
    title=dict(text='Relación entre Empaque y Edad del Producto',
               font=dict(family="Roboto", size=20, color='black'))
    # xaxis_title='Mes',
    # xaxis=dict(title_font=dict(family="Roboto", size=18, color='black')),
    # yaxis_title='Edad del Producto',
    # yaxis=dict(title_font=dict(family="Roboto", size=18, color='black')),
    # xaxis=dict(range=[0.5, 12.5], dtick=1)
)
st.plotly_chart(fig_box)

st.info(
    "Descripción grafico por Empaque. ")

# Gráfico de linea por ciudad
# --------------------------------------------------------
df_grp_ret = filtered_df.groupby(['mes_encuesta', 'Ciudad'])['Edad_producto'].mean().reset_index()
colors = ['#636EFA', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
fig_line_ret = px.line(df_grp_ret, x='mes_encuesta', y='Edad_producto', color='Ciudad', 
              title='Promedio Mensual de Frescura por Ciudad',
              labels={'Mes': 'Mes', 'Frescura': 'Frescura'},
              color_discrete_sequence=colors)

fig_line_ret.update_xaxes(range=[0.5, 12.5], dtick=1)

# Aplicar Roboto al título y centrarlo, ajustando también el tamaño y color de la fuente
fig_line_ret.update_layout(
    title=dict(text='Promedio Mensual de Frescura por Ciudad',
               font=dict(family="Roboto", size=20, color="black")), 
    xaxis=dict(title='Mes', title_font=dict(family="Roboto", size=18, color="black"), range=[0.5, 12.5], dtick=1),
    yaxis=dict(title='Frescura', title_font=dict(family="Roboto", size=18, color="black"))
)
st.plotly_chart(fig_line_ret)

st.info(
    "Descripción grafico por Ciudad. ")

# Gráfico de linea por retornabilidad
# --------------------------------------------------------


# df_grp_ret = filtered_df.groupby(['mes_encuesta', 'Retornable'])['Edad_producto'].mean().reset_index()

# Definiendo el mapa de colores para las categorías 'Sí' y 'No'
# color_discrete_map_2 = {'Sí': '#E2E062', 'No': '#297159'}  # Reemplaza estos colores con los que desees

# fig_line_ret = px.line(df_grp_ret, x='mes_encuesta', y='Edad_producto', color='Retornable', 
              # title='Promedio Mensual de Frescura por Retornabilidad',
              # labels={'mes_encuesta': 'Mes', 'Edad_producto': 'Frescura'},
              # color_discrete_map=color_discrete_map_2)
              
# fig_line_ret.update_xaxes(range=[0.5, 12.5], dtick=1)
# st.plotly_chart(fig_line_ret)



df_grp_ret = filtered_df.groupby(['mes_encuesta', 'Retornable'])['Edad_producto'].mean().reset_index()

# Inicializa una figura
fig_line_ret = go.Figure()

# Colores específicos para cada categoría
color_map = {'SI': '#E2E062', 'No': '#297159'}

# Agrega las líneas manualmente
for retornable, group in df_grp_ret.groupby('Retornable'):
    fig_line_ret.add_trace(go.Scatter(x=group['mes_encuesta'], y=group['Edad_producto'],
                                      name=retornable,
                                      mode='lines',
                                      line=dict(color=color_map[retornable])))

# Configura el título y las etiquetas de los ejes
fig_line_ret.update_layout(title='Promedio Mensual de Frescura por Retornabilidad',
                           xaxis_title='Mes',
                           yaxis_title='Frescura',
                           xaxis=dict(range=[0.5, 12.5], dtick=1))

# Configura el título y las etiquetas de los ejes con la fuente Roboto y centra el título
fig_line_ret.update_layout(
    title=dict(text='Promedio Mensual de Frescura por Retornabilidad',
               font=dict(family="Roboto", size=20, color="black"))
    # xaxis_title='Mes',
    # xaxis=dict(title_font=dict(family="Roboto", size=18, color="black"), range=[0.5, 12.5], dtick=1),
    # yaxis_title='Frescura',
    # yaxis=dict(title_font=dict(family="Roboto", size=18, color="black"))
)                           

# Muestra el gráfico
st.plotly_chart(fig_line_ret)

st.info(
    "Descripción grafico por Distribución y top 10. ")

# División en columnas
# --------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    # Gráfico de pie
    conteo_frescura = filtered_df['Frescura'].value_counts()
    fig_pie = px.pie(names=conteo_frescura.index, values=conteo_frescura.values, title='Distribución de Frescura')
    # Actualiza los colores de las partes del gráfico de pie manualmente usando color_discrete_map
    fig_pie.update_traces(marker=dict(colors=[color_discrete_map[name] for name in conteo_frescura.index]))
    
    fig_pie.update_layout(
    title_font=dict(family="Roboto", size=20, color="black"),
    width=350,
    height=350
)
    st.plotly_chart(fig_pie)
    
    # Descripción grafico por Canal
    
with col2:    
    # Crear el gráfico de barras para el top 10 de canales con frescura 'Inaceptable'    
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
        color_discrete_sequence=['#297159']  # Esto cambiará el color de las barras a rojo
    )
    
    # Actualizar el gráfico para mostrar los valores en las barras
    fig_bar.update_traces(
    texttemplate='%{y}',  # Muestra el valor de 'y' (Cantidad) en cada barra
    textposition='outside'  # Coloca el texto fuera de las barras para evitar solapamientos
)
    
    # Aplicar Roboto al título 
    fig_bar.update_layout(
    title_font=dict(family="Roboto", size=18, color="black"),
    width=350,
    height=350
)
    fig_bar.update_layout(width=350, height=350)
    st.plotly_chart(fig_bar)   

# Descripción grafico por Canal
st.info(
    "Descripción grafico por Distribución y top 10. ")    
    
# Gráfico funnel por frescura / canal
df_frescura_canal = datos.groupby(['Frescura', 'Canal']).size().reset_index(name= 'Cantidad')
fig_funnel = px.funnel(df_frescura_canal, 
                       x = 'Cantidad', 
                       y = 'Canal', 
                       color = 'Frescura',
                       title = 'Distribución de Frescura por Canal',
                       color_discrete_map=color_discrete_map,
                       category_orders=category_orders)

# Actualizar la fuente del título
fig_funnel.update_layout(title_font=dict(family="Roboto", size=20, color="black"))
st.plotly_chart(fig_funnel)

# Descripción grafico por Canal
st.info(
    "Descripción grafico por canal. ")




#Prueba de commit Santiago