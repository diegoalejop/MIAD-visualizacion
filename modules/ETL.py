import pandas as pd

#datos = pd.read_excel(r"C:\Users\dapen\OneDrive - Universidad de los andes\MIAD\Visualización y Storytelling\MIAD-visualizacion\Datos.xlsx",
                      #sheet_name='Export')
                      
# datos = pd.read_excel(r"D:\Maestria_Andes_2023\Ciclo_3\Visualización y storytelling\6.Semana\MIAD-visualizacion\Datos.xlsx",
                      #sheet_name='Export')
datos = pd.read_excel("../Datos.xlsx", sheet_name='Export')

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