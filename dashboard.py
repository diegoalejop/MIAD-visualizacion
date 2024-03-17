import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import time
import folium
from streamlit_folium import folium_static

# Inyectar CSS para cambiar el color de fondo utilizando st.markdown
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');

    .stApp {
        background-color: #F5F7F8;
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

def calculo_canal(row):
    if row['Canal'] in ['Bar Estandar', 
                        'Entretenimiento',
                        'Tienda con consumo',
                        'Tienda de Barrio']:
        return 'ON'
    else:
        return 'OFF'
    
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
datos['Canal'] = datos.apply(calculo_canal, axis = 1)

# Crear columnas con límite "Debe Mejorar" e "Inaceptable" para cada Marca

datos['Lim_debe_mejorar'] = pd.NA
datos['Lim_inaceptable'] = pd.NA

datos.loc[datos['Marca'].isin(['Marca_1', 'Marca_2', 'Marca_3']), 'Lim_debe_mejorar'] = 90
datos.loc[datos['Marca'].isin(['Marca_1', 'Marca_2', 'Marca_3']), 'Lim_inaceptable'] = 120

datos.loc[datos['Marca'].isin(['Marca_4', 'Marca_5', 'Marca_6', 'Marca_7']), 'Lim_debe_mejorar'] = 60
datos.loc[datos['Marca'].isin(['Marca_4', 'Marca_5', 'Marca_6', 'Marca_7']), 'Lim_inaceptable'] = 100

df = datos


#########
# Sidebar
st.sidebar.title('Filtros del reporte')
st.sidebar.header("Filtra el reporte de acuerdo con tu selección:")

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
año_select = st.sidebar.selectbox('Selecciona años de producción:', año_unico)
ciudad_select = st.sidebar.multiselect('Selecciona una o más ciudades:', ciudad_unico)
marca_select = st.sidebar.multiselect('Selecciona una marca:', marca_unico)
canal_select = st.sidebar.multiselect('Selecciona uno o más canales:', canal_unico)

if not canal_select and not ciudad_select and not marca_select: 
    # Si no se seleccionó ningún canal, ciudad o marca, filtrar solo por año
    filtered_df = df[df['año_produccion'] == año_select]
else:
    # Aplicar filtros basados en selecciones
    filtered_df = df[df['año_produccion'] == año_select]
    if marca_select:  # Si se seleccionaron marcas
        filtered_df = filtered_df[filtered_df['Marca'].isin(marca_select)]
    if canal_select:  # Si se seleccionaron canales
        filtered_df = filtered_df[filtered_df['Canal'].isin(canal_select)]
    if ciudad_select:  # Si se seleccionaron ciudades
        filtered_df = filtered_df[filtered_df['Ciudad'].isin(ciudad_select)]
    
#Créditos
st.sidebar.write('Realizado por los cuenteros de la MIAD (c)')
# Fecha de datos   
st.sidebar.write('Datos del mercado de Abril 2021 - Diciembre 2023')


# Contenido
# --------------------------------------------------------
    
## Hoja de descripción
# Crear contenedores para los tabs
# Título del dashboard
st.title('¿Qué tan :green[fresco] es lo que consumes?')

#Descripción del dashboard
st.write("La evaluación de la frescura para las empresas de consumo" 
         "masivo, es fundamental para determinar la calidad de los"
         "productos en el mercado, su nivel de aceptación y planificar "
         "su producción futura. Diversas condiciones y circunstancias"
         "pueden influir en esta evaluación, por lo que comprenderlas "
         "puede resultar beneficioso para tu próxima adquisición.")

st.write("Para abordar estas cuestiones, las plantas productoras"
         "realizan muestreos periódicos de frescura, los cuales"
         "constituyen de nuestra principal fuente de información para"
         "este informe..")

#Descripción de frescura
st.header('¿Cómo se mide la :green[frescura?]', divider='green')

st.write("La frescura se evalúa a través del tiempo en días que lleva el producto en el mercado desde su "
            "producción. Productos que lleven mucho tiempo en las repisas se consideran menos frescos, por lo "
            "que suelen tener una calidad más baja. Algunos llegan a tener calidades inaceptables al llevar mucho "
            "tiempo sin ser consumidos. \n"
            "A continuación puedes ver el resumen en días de frescura: ")

    
df_describe = filtered_df[['Edad_producto']].describe().round(1)
media = df_describe.loc['mean', 'Edad_producto']
cantidad = df_describe.loc['count', 'Edad_producto']
std = df_describe.loc['std', 'Edad_producto']
min = df_describe.loc['min', 'Edad_producto'] 
max = df_describe.loc['max', 'Edad_producto'] 
    
#Tarjetas de resumen
col1, col2, col3, col4 = st.columns(4)
col1.metric("Edad Promedio", str(media))
col2.metric("Edad Mínima", str(min))
col3.metric("Edad Máxima", str(max))
col4.metric("Desviación", str(std))

st.header('Revisa los siguientes conceptos importantes:', divider='green')

col1, col2, col3, col4 = st.columns(4)

with col1:
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
    if st.button("Edad de producto1"):
        st.write_stream(stream_data)

with col2:   
    desc_calidad = """
        La frescura se puede desagregar en clasificaciones de calidad de los productos: \n
        Ideal: lleva menos de 60 dias en el mercado  \n
        Debe mejorar: lleva entre 60 y 100 días en el mercado \n
        Inacetable: lleva más de 120 dias en el mercado
        """
    def stream_data2():
        for word in desc_calidad.split(" "):
            yield word + " "
            time.sleep(0.02)
    if st.button("Calidad"):
        st.write_stream(stream_data2)
        
with col3:
    desc_retornabilidad = """
        La retornabilidad de envases fomenta la reutilización 
        de recipientes, reduciendo la necesidad de producir 
        nuevos y disminuyendo así los costos de materiales y 
        gestión de residuos. Este sistema no solo aporta 
        beneficios ambientales significativos, sino que también 
        ofrece ventajas económicas para empresas y consumidores 
        mediante la reducción de gastos y el incentivo de devoluciones
        a través de sistemas de depósito-reembolso. 
        Además, contribuye a la sustentabilidad de la 
        cadena de suministro y fortalece la imagen de marca 
        comprometida con prácticas ecológicas.
        """
    def stream_data3():
        for word in desc_retornabilidad.split(" "):
            yield word + " "
            time.sleep(0.02)

    if st.button("Retornabilidad"):
        st.write_stream(stream_data3)

with col4:
    desc_canal = """
        Los canales de venta se dividen en dos principales grupos:
        1. On Trade: Se refiere a la venta de bebidas alcohólicas
        para ser consumidas en el mismo lugar de compra. Por ejemplo:
        bares, tiendas de barrio, restaurantes y clubes.
        2. Off Trade: Se refiere a la venta e bebidas alcohólicas 
        para ser consumidas fuera del lugar de compra. 
        Este canal abarca supermercados y licorerías
        """
    def stream_data4():
        for word in desc_canal.split(" "):
            yield word + " "
            time.sleep(0.02)

    if st.button("Canal"):
        st.write_stream(stream_data4)        

#Mapa por ciudad
df_ciudad = filtered_df.groupby(['Ciudad'])['Edad_producto'].describe().reset_index()[['Ciudad','mean']]
df_ciudad.rename(columns={'mean':'Edad'}, inplace=True)

#Colores asignados por clasificación
limites_clas = [
    (df_ciudad['Edad'] < 90),
    ((df_ciudad['Edad'] >=90) & (df_ciudad['Edad'] <=110) ),
    (df_ciudad['Edad'] > 110)
]

colores = ['#BFB445','#64954D','#0C5951']
df_ciudad['Color'] = np.select(limites_clas,colores)

# Función para convertir el color hexadecimal a un formato compatible con Folium
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Crear un mapa centrado en Colombia
mapa = folium.Map(location=[4.7, -76], zoom_start=7.49)

# Añadir marcadores para cada ciudad con el tamaño proporcional al valor y color personalizado
for index, row in df_ciudad.iterrows():
    ciudad = row['Ciudad']
    valor = row['Edad']
    color_hex = row['Color']
    color_rgb = hex_to_rgb(color_hex)
    
    # Determinar la ubicación de la ciudad
    if ciudad == 'Bogotá':
        location = [4.6097, -74.0817]
    elif ciudad == 'Cali':
        location = [3.4516, -76.5320]
    elif ciudad == 'Medellín':
        location = [6.2442, -75.5812]
    
    folium.CircleMarker(
        location=location,
        radius=valor/1.5,
        color=color_hex,
        fill=True,
        fill_color=color_hex,
        fill_opacity=0.6,
        popup=f'{ciudad}: {valor}'
    ).add_to(mapa)

st.header('Frescura en las principales ciudades de Colombia')
#st.write('Valores representados por el tamaño de las esferas')
folium_static(mapa)

st.header('Análisis de resultados', divider= 'green',help="Recuerda revisar las explicaciones para cada gráfico")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Análisis General", "Tipo de Empaque", "Ciudad", "Retornabilidad", "Canal"], )
with tab1: # Tendencia general
    st.write("Muestra con frescura mínima")
    # Obtención del valor mínimo    
    indice_minimo = filtered_df['Edad_producto'].idxmin()
    min_eproducto = filtered_df.at[indice_minimo, 'Edad_producto']
    min_empaque = filtered_df.at[indice_minimo, 'Empaque']
    min_canal = filtered_df.at[indice_minimo, 'Canal']
    
    #Tarjetas de resumen mínimo
    col1, col2, col3 = st.columns(3)
    col1.metric("Edad Promedio", str(min_eproducto))
    col2.metric("Canal", str(min_canal))
    col3.metric("Empaque", str(min_empaque))   
    
    explicacion_general = '''
    Un análisis exhaustivo de los datos revela el 
    comportamiento global de la frescura y su evolución a lo 
    largo del año. Los valores mínimos de edad de producto 
    indican una rotación más rápida en el mercado. 
    No obstante, para un análisis más detallado, es 
    fundamental profundizar en variables como:
    - Tipo de empaque.
    - Ciudad.
    - Retornabilidad.
    - Canal de distribución.
    
    Estos factores son clave para comprender mejor las 
    dinámicas y tendencias subyacentes en el comportamiento 
    de la frescura y su relación con otros aspectos del mercado. 
    '''
    
    with st.expander("📕 Ver explicación"):
        st.markdown(explicacion_general)    
    
    datos_linea_g = filtered_df.groupby('mes_encuesta')['Edad_producto'].agg(['mean', 'std']).reset_index()
    fig_line_g = go.Figure()
    # Línea de la media
    fig_line_g.add_trace(go.Scatter(
        x=datos_linea_g['mes_encuesta'].astype(str),
        y=datos_linea_g['mean'],
        mode='lines+markers',
        name='Media de Frescura',
        showlegend=False,
        line = dict(color = 'rgb(0,97,57,1)')        
    ))

    # Banda de error para la desviación estándar
    fig_line_g.add_trace(go.Scatter(
        x=pd.concat([datos_linea_g['mes_encuesta'], datos_linea_g['mes_encuesta'][::-1]]).astype(str),
        y=pd.concat([datos_linea_g['mean'] + datos_linea_g['std']/20, (datos_linea_g['mean'] - datos_linea_g['std']/20)[::-1]]),
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(0,97,57,0)'),
        hoverinfo="skip",
        showlegend=False
    ))

    # Actualizar layout para quitar la leyenda (no es necesario ya que se aplicó showlegend=False en cada traza)
    fig_line_g.update_layout(
        title='Tendencia Mensual de la Frescura',
        title_font=dict(family="Roboto", size=20, color="black"),
        xaxis_title='Mes',
        yaxis_title='Frescura'
    )

    st.plotly_chart(fig_line_g)
    
    color_discrete_map = {
    'Ideal': '#45875e',  
    'Debe Mejorar': '#e2e062',  
    'Inaceptable': '#FF9B9B'}
    
    conteo_frescura = filtered_df['Frescura'].value_counts()
    fig_pie = px.pie(names=conteo_frescura.index, 
                     values=conteo_frescura.values, 
                     title='Distribución de Frescura',
                     color_discrete_map=color_discrete_map)
    fig_pie.update_traces(marker=dict(colors=[color_discrete_map[name] for name in conteo_frescura.index]))
    fig_pie.update_layout(
    title_font=dict(family="Roboto", size=20, color="black"),
    width=350,
    height=350
    )
    st.plotly_chart(fig_pie)
       
with tab2: # Tipo de empaque
    explicacion_empaque = '''
    El análisis de frescura por tipo de empaque proporciona 
    una visión detallada del rendimiento de botellas y latas 
    en el mercado. Esta información es crucial, ya que nos permite 
    entender qué tipo de empaque está experimentando una mayor 
    rotación y, en consecuencia, nos ayuda a planificar de 
    manera efectiva la producción en función de la demanda observada. 
    Además, al profundizar en esta variable, podemos identificar 
    tendencias estacionales o preferencias de los consumidores 
    que impactan directamente en las estrategias de fabricación y 
    distribución de productos frescos.    
    '''
    
    with st.expander("📕 Ver explicación"):
        st.markdown(explicacion_empaque)
    
    
    fig_line_te = go.Figure()
    datos_linea_emp = filtered_df.groupby(['mes_encuesta', 'Empaque'])['Edad_producto'].agg(['mean', 'std']).reset_index()

    for empaque in datos_linea_emp['Empaque'].unique():
        df_empaque = datos_linea_emp[datos_linea_emp['Empaque'] == empaque]
        
        
        fillcolor_empaque = {
            'Botella': 'rgba(0,97,55, 0.4)',  
            'Lata': 'rgba(195,192,0, 0.4)'  
        }.get(empaque, 'rgba(0, 0, 0, 0.4)') 

        # Línea de la media para cada empaque
        fig_line_te.add_trace(go.Scatter(
            x=df_empaque['mes_encuesta'].astype(str),
            y=df_empaque['mean'],
            mode='lines+markers',
            name=f'{empaque}',
            line=dict(color=fillcolor_empaque)  
        ))

        # Agregar banda de error para la desviación estándar
        fig_line_te.add_trace(go.Scatter(
            x=pd.concat([df_empaque['mes_encuesta'], df_empaque['mes_encuesta'][::-1]]).astype(str),
            y=pd.concat([df_empaque['mean'] + df_empaque['std']/20, (df_empaque['mean'] - df_empaque['std']/20)[::-1]]),
            fill='toself',
            fillcolor=fillcolor_empaque, 
            line=dict(color='rgba(255,255,255,0)'),  
            showlegend=False,  
            hoverinfo="skip"
        ))
        
    fig_line_te.update_layout(
        title='Tendencia Mensual de la Frescura por Empaque',
        title_font=dict(family="Roboto", size=20, color="black"),
        xaxis_title='Mes',
        yaxis_title='Frescura',
        legend_title="Empaque"
    )

    st.plotly_chart(fig_line_te)
    
    df_frescura_empaque = filtered_df.groupby(['Frescura', 'Empaque']).size().reset_index(name= 'Cantidad')
    fig_funnel_empaque = px.funnel(df_frescura_empaque, 
                    x = 'Cantidad', 
                    y = 'Empaque', 
                    color = 'Frescura',
                    title = 'Distribución de Frescura por Empaque',
                    color_discrete_map=color_discrete_map,
                    category_orders=category_orders
                )

    # Actualizar la fuente del título
    fig_funnel_empaque.update_layout(title_font=dict(family="Roboto", size=20, color="black"))
    st.plotly_chart(fig_funnel_empaque)

with tab3: # Ciudad
    explicacion_ciudad = '''
    El análisis de frescura por ciudad es fundamental 
    para comprender el comportamiento de nuestros productos 
    en el mercado en cada una de las zonas geográficas. 
    Por ejemplo, en zonas calurosas como Cali, el consumo de bebidas 
    puede diferir significativamente en comparación con ciudades 
    de clima frío como Bogotá. Esto se debe a que los consumidores 
    en áreas cálidas tienden a preferir bebidas refrescantes y 
    sin astringencia, mientras que los consumidores en climas fríos 
    pueden tener preferencias diferentes. 
    
    Por lo tanto, entender las preferencias regionales 
    nos permite adaptar nuestras estrategias de producción, 
    distribución y marketing de manera más precisa, 
    maximizando así la satisfacción del cliente y 
    la eficacia de nuestras operaciones comerciales. 
    '''
    
    with st.expander("Ver explicación"):
        st.markdown(explicacion_ciudad)
    
    
    fig_line_c = go.Figure()
    datos_linea_ciu = filtered_df.groupby(['mes_encuesta', 'Ciudad'])['Edad_producto'].agg(['mean', 'std']).reset_index()

    for ciudad in datos_linea_ciu['Ciudad'].unique():
        df_ciudad = datos_linea_ciu[datos_linea_ciu['Ciudad'] == ciudad]
        
        # Definir colores de fillcolor para la banda de error basados en el empaque
        fillcolor_ciudad = {
            'Bogotá': 'rgba(0,97,55, 0.4)',  
            'Cali': 'rgba(195,192,0, 0.4)',
            'Medellín': 'rgba(250,70,22,0.4)'
        }.get(ciudad, 'rgba(0, 0, 0, 0.4)') 

        # Línea de la media para cada empaque
        fig_line_c.add_trace(go.Scatter(
            x=df_ciudad['mes_encuesta'].astype(str),
            y=df_ciudad['mean'],
            mode='lines+markers',
            name=f'{ciudad}',
            line=dict(color=fillcolor_ciudad)  
        ))

        # Agregar banda de error para la desviación estándar
        fig_line_c.add_trace(go.Scatter(
            x=pd.concat([df_ciudad['mes_encuesta'], df_ciudad['mes_encuesta'][::-1]]).astype(str),
            y=pd.concat([df_ciudad['mean'] + df_ciudad['std']/10, (df_ciudad['mean'] - df_ciudad['std']/10  )[::-1]]),
            fill='toself',
            fillcolor=fillcolor_ciudad, 
            line=dict(color='rgba(255,255,255,0)'),  
            showlegend=False,  
            hoverinfo="skip"
        ))
        
    # Configuración del layout del gráfico, incluyendo la leyenda
    fig_line_c.update_layout(
        title='Tendencia Mensual de la Frescura por Ciudad',
        title_font=dict(family="Roboto", size=20, color="black"),
        xaxis_title='Mes',
        yaxis_title='Frescura',
        legend_title='Ciudad',
        template='plotly_dark'
    )
    
    st.plotly_chart(fig_line_c)
    
    df_frescura_ciudad = filtered_df.groupby(['Frescura', 'Ciudad']).size().reset_index(name= 'Cantidad')
    fig_funnel_ciudad = px.funnel(df_frescura_ciudad, 
                    x = 'Cantidad', 
                    y = 'Ciudad', 
                    color = 'Frescura',
                    title = 'Distribución de Frescura por Ciudad',
                    color_discrete_map=color_discrete_map,
                    category_orders=category_orders
                )

    # Actualizar la fuente del título
    fig_funnel_ciudad.update_layout(title_font=dict(family="Roboto", size=20, color="black"))
    st.plotly_chart(fig_funnel_ciudad)

    with st.expander("Ver explicación"):
        st.markdown("*Streamlit* is **really** ***cool***.")
    
with tab4: # Retornabilidad
    explicacion_retornabilidad = '''
        El análisis del efecto de la retornabilidad en la 
        frescura de nuestros productos es de suma 
        importancia para comprender cómo influye el ciclo de 
        reutilización en la percepción del consumidor y 
        en la calidad del producto. 
        
        La implementación de envases retornables puede tener 
        un impacto significativo en la sostenibilidad ambiental 
        y financiera. Por un lado, la utilización 
        de envases retornables puede reducir la generación de 
        residuos y promover prácticas más ecológicas 
        dentro de la cadena de suministro. Por otro lado,
        la sostenibilidad financiera que genera la retornabilidad en una
        empresa de consumo masivo representa ahorro significativo
        al momento de utilizar envases retornables ya que estos representan
        cerca del 30 "%"" del valor del producto.
   
    '''
    
    with st.expander("📕 Ver explicación"):
        st.markdown(explicacion_retornabilidad)    
    
    fig_line_r = go.Figure()
    datos_linea_r = filtered_df.groupby(['mes_encuesta', 'Retornable'])['Edad_producto'].agg(['mean', 'std']).reset_index()

    for retornable in datos_linea_r['Retornable'].unique():
        df_ret = datos_linea_r[datos_linea_r['Retornable'] == retornable]        
        # Definir colores de fillcolor para la banda de error basados en el empaque
        fillcolor_r = {
            'SI': 'rgba(0,97,55, 0.4)',  
            'No': 'rgba(195,192,0, 0.4)'
        }.get(retornable, 'rgba(0, 0, 0, 0.4)') 

        # Línea de la media para cada empaque
        fig_line_r.add_trace(go.Scatter(
            x=df_ret['mes_encuesta'].astype(str),
            y=df_ret['mean'],
            mode='lines+markers',
            name=f'{retornable}',
            line=dict(color=fillcolor_r)  
        ))

        # Agregar banda de error para la desviación estándar
        fig_line_r.add_trace(go.Scatter(
            x=pd.concat([df_ret['mes_encuesta'], df_ret['mes_encuesta'][::-1]]).astype(str),
            y=pd.concat([df_ret['mean'] + df_ret['std']/10, (df_ret['mean'] - df_ret['std']/10  )[::-1]]),
            fill='toself',
            fillcolor=fillcolor_r, 
            line=dict(color='rgba(255,255,255,0)'),  
            showlegend=False,  
            hoverinfo="skip"
        ))
        
    # Configuración del layout del gráfico, incluyendo la leyenda
    fig_line_r.update_layout(
        title='Tendencia Mensual de la Frescura por Retornabilidad',
        title_font=dict(family="Roboto", size=20, color="black"),
        xaxis_title='Mes',
        yaxis_title='Frescura',
        legend_title='Retornabilidad'
    )

    st.plotly_chart(fig_line_r)
    
    df_frescura_ret = filtered_df.groupby(['Frescura', 'Retornable']).size().reset_index(name= 'Cantidad')
    fig_funnel_ret = px.funnel(df_frescura_ret, 
                    x = 'Cantidad', 
                    y = 'Retornable', 
                    color = 'Frescura',
                    title = 'Distribución de Frescura por Retornabilidad',
                    color_discrete_map=color_discrete_map,
                    category_orders=category_orders
                )

    # Actualizar la fuente del título
    fig_funnel_ret.update_layout(title_font=dict(family="Roboto", size=20, color="black"))
    st.plotly_chart(fig_funnel_ret)    

    with st.expander("Ver explicación"):
        st.markdown("*Streamlit* is **really** ***cool***.")
    
with tab5: # Canal
    explicacion_canal = '''
    El análisis de los tipos de canales de distribución, 
    como el on-trade y el off-trade, es esencial para comprender 
    cómo varía la frescura y la demanda de nuestros 
    productos en diferentes contextos de consumo.
    
    El canal on-trade se enfoca en la frescura inmediata y la 
    calidad percibida, ya que los consumidores esperan productos 
    frescos en establecimientos como bares y restaurantes. 
    Por otro lado, en el canal off-trade, la frescura sigue 
    siendo importante, pero también se valoran aspectos como 
    la durabilidad del producto y la presentación del empaque, 
    ya que los consumidores compran para consumir en casa. 
    Analizar estos canales nos permite adaptar estrategias 
    de producción y distribución para mantener la frescura y 
    satisfacción del cliente en ambos contextos de consumo.
    '''
    
    with st.expander("📕 Ver explicación"):
        st.markdown(explicacion_canal)
        
    fig_line_canal = go.Figure()
    datos_linea_canal = filtered_df.groupby(['mes_encuesta', 'Canal'])['Edad_producto'].agg(['mean', 'std']).reset_index()

    for canal in datos_linea_canal['Canal'].unique():
        df_canal = datos_linea_canal[datos_linea_canal['Canal'] == canal]        
        # Definir colores de fillcolor para la banda de error basados en el empaque
        fillcolor_canal = {
            'ON': 'rgba(0,97,55, 0.4)',  
            'OFF': 'rgba(195,192,0, 0.4)'
        }.get(canal, 'rgba(0, 0, 0, 0.4)') 

        # Línea de la media para cada empaque
        fig_line_canal.add_trace(go.Scatter(
            x=df_canal['mes_encuesta'].astype(str),
            y=df_canal['mean'],
            mode='lines+markers',
            name=f'{canal}',
            line=dict(color=fillcolor_canal)  
        ))

        # Agregar banda de error para la desviación estándar
        fig_line_canal.add_trace(go.Scatter(
            x=pd.concat([df_canal['mes_encuesta'], df_canal['mes_encuesta'][::-1]]).astype(str),
            y=pd.concat([df_canal['mean'] + df_canal['std']/10, (df_canal['mean'] - df_canal['std']/10  )[::-1]]),
            fill='toself',
            fillcolor=fillcolor_canal, 
            line=dict(color='rgba(255,255,255,0)'),  
            showlegend=False,  
            hoverinfo="skip"
        ))
        
    # Configuración del layout del gráfico, incluyendo la leyenda
    fig_line_canal.update_layout(
        title='Tendencia Mensual de la Frescura por Canal',
        title_font=dict(family="Roboto", size=20, color="black"),
        xaxis_title='Mes',
        yaxis_title='Frescura',
        legend_title='Canal'
    )

    st.plotly_chart(fig_line_canal)
    
    df_frescura_canal = filtered_df.groupby(['Frescura', 'Canal']).size().reset_index(name= 'Cantidad')
    fig_funnel_canal = px.funnel(df_frescura_canal, 
                    x = 'Cantidad', 
                    y = 'Canal', 
                    color = 'Frescura',
                    title = 'Distribución de Frescura por Canal',
                    color_discrete_map=color_discrete_map,
                    category_orders=category_orders
                )

    # Actualizar la fuente del título
    fig_funnel_canal.update_layout(title_font=dict(family="Roboto", size=20, color="black"))
    st.plotly_chart(fig_funnel_canal)

    with st.expander("Ver explicación"):
        st.markdown("*Streamlit* is **really** ***cool***.")