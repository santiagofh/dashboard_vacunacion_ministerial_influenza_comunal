# Importar librerías
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Función para leer el último archivo creado con el nombre Reporte_vacunas_privadas en la carpeta "Reporte"
def leer_ultimo_reporte_vacunas_privadas(directorio):
    # Buscar todos los archivos en el directorio que contengan "Reporte_vacunas_privadas"
    archivos = [os.path.join(directorio, f) for f in os.listdir(directorio) if "Reporte_vacunas_privadas" in f and f.endswith(".csv")]
    
    # Si no se encuentran archivos, devolver None
    if not archivos:
        return None, None
    
    # Encontrar el archivo más reciente basado en la fecha de modificación
    ultimo_archivo = max(archivos, key=os.path.getmtime)
    
    # Leer el archivo CSV
    df = pd.read_csv(ultimo_archivo)
    
    # Obtener la fecha de creación del archivo desde el nombre del archivo
    nombre_archivo = os.path.basename(ultimo_archivo)
    fecha_creacion_str = nombre_archivo.split('_')[0]
    fecha_creacion = datetime.strptime(fecha_creacion_str, '%Y%m%d')
    
    return df, fecha_creacion

# Directorio de los reportes
directorio_reporte = 'Reporte'

# Leer el último reporte de vacunas privadas
ultimo_reporte, fecha_creacion = leer_ultimo_reporte_vacunas_privadas(directorio_reporte)
ultimo_reporte = ultimo_reporte.loc[(ultimo_reporte['Nombre Dependencia Jerárquica'] == 'SEREMI Metropolitana de Santiago')
                                    |
                                    (ultimo_reporte['Nombre Dependencia Jerárquica'] == 'Ministerio de Salud')]

# Mostrar el DataFrame en Streamlit si se encuentra un archivo
if ultimo_reporte is not None:
    st.title("Reporte de Vacunaciones Privadas")
    st.write(f"Último Reporte de Vacunas Privadas (Creado el {fecha_creacion.strftime('%Y-%m-%d')}):")
    st.write("Nota: El separador de miles es ',' y el separador decimal es '.'. Este reporte fue generado por el Subdepartamento de gestión de la información y estadística de la Seremi de Salud de la Región Metropolitana.")
    
    # Seleccionar comunas
    todas_comunas = ["Todas las comunas"] + list(ultimo_reporte['COMUNA_OCURR'].unique())
    comunas_seleccionadas = st.multiselect("Seleccione las comunas para mostrar:", options=todas_comunas, default="Todas las comunas")
    
    # Filtrar el DataFrame según las comunas seleccionadas
    if "Todas las comunas" in comunas_seleccionadas:
        reporte_filtrado = ultimo_reporte
    else:
        reporte_filtrado = ultimo_reporte[ultimo_reporte['COMUNA_OCURR'].isin(comunas_seleccionadas)]
    
    st.dataframe(reporte_filtrado.reset_index(drop=True))

    # Agrupar por comuna y sumar las vacunaciones
    suma_por_comuna = reporte_filtrado.groupby('COMUNA_OCURR','ESTABLECIMIENTO').agg(
        vacunacion_ultimos_3_dias=('vacunacion_ultimos_3_dias', 'sum'),
        vacunacion_ultimos_7_dias=('vacunacion_ultimos_7_dias', 'sum'),
        vacunacion_ultimos_14_dias=('vacunacion_ultimos_14_dias', 'sum')
    ).reset_index()

    # Calcular los promedios, medianas y medias por día
    suma_por_comuna['promedio_por_dia_3'] = suma_por_comuna['vacunacion_ultimos_3_dias'] / 3
    suma_por_comuna['promedio_por_dia_7'] = suma_por_comuna['vacunacion_ultimos_7_dias'] / 7
    suma_por_comuna['promedio_por_dia_14'] = suma_por_comuna['vacunacion_ultimos_14_dias'] / 14

    suma_por_comuna['mediana_por_dia_3'] = reporte_filtrado.groupby('COMUNA_OCURR','ESTABLECIMIENTO')['vacunacion_ultimos_3_dias'].median() / 3
    suma_por_comuna['mediana_por_dia_7'] = reporte_filtrado.groupby('COMUNA_OCURR','ESTABLECIMIENTO')['vacunacion_ultimos_7_dias'].median() / 7
    suma_por_comuna['mediana_por_dia_14'] = reporte_filtrado.groupby('COMUNA_OCURR','ESTABLECIMIENTO')['vacunacion_ultimos_14_dias'].median() / 14

    suma_por_comuna['media_por_dia_3'] = reporte_filtrado.groupby('COMUNA_OCURR','ESTABLECIMIENTO')['vacunacion_ultimos_3_dias'].mean() / 3
    suma_por_comuna['media_por_dia_7'] = reporte_filtrado.groupby('COMUNA_OCURR','ESTABLECIMIENTO')['vacunacion_ultimos_7_dias'].mean() / 7
    suma_por_comuna['media_por_dia_14'] = reporte_filtrado.groupby('COMUNA_OCURR','ESTABLECIMIENTO')['vacunacion_ultimos_14_dias'].mean() / 14

    # Mostrar DataFrames y gráficos
    st.subheader("Suma de Vacunaciones por Comuna")
    st.dataframe(suma_por_comuna)
    fig_suma = px.bar(suma_por_comuna, x='COMUNA_OCURR', y=['vacunacion_ultimos_3_dias', 'vacunacion_ultimos_7_dias', 'vacunacion_ultimos_14_dias'], barmode='group', title="Suma de Vacunaciones por Comuna")
    st.plotly_chart(fig_suma)

    st.subheader("Promedio de Vacunaciones por Día y por Comuna")
    st.dataframe(suma_por_comuna[['COMUNA_OCURR', 'promedio_por_dia_3', 'promedio_por_dia_7', 'promedio_por_dia_14']])
    fig_promedio = px.bar(suma_por_comuna, x='COMUNA_OCURR', y=['promedio_por_dia_3', 'promedio_por_dia_7', 'promedio_por_dia_14'], barmode='group', title="Promedio de Vacunaciones por Día y por Comuna")
    st.plotly_chart(fig_promedio)

    st.subheader("Mediana de Vacunaciones por Día y por Comuna")
    st.dataframe(suma_por_comuna[['COMUNA_OCURR', 'mediana_por_dia_3', 'mediana_por_dia_7', 'mediana_por_dia_14']])
    fig_mediana = px.bar(suma_por_comuna, x='COMUNA_OCURR', y=['mediana_por_dia_3', 'mediana_por_dia_7', 'mediana_por_dia_14'], barmode='group', title="Mediana de Vacunaciones por Día y por Comuna")
    st.plotly_chart(fig_mediana)

    st.subheader("Media de Vacunaciones por Día y por Comuna")
    st.dataframe(suma_por_comuna[['COMUNA_OCURR', 'media_por_dia_3', 'media_por_dia_7', 'media_por_dia_14']])
    fig_media = px.bar(suma_por_comuna, x='COMUNA_OCURR', y=['media_por_dia_3', 'media_por_dia_7', 'media_por_dia_14'], barmode='group', title="Media de Vacunaciones por Día y por Comuna")
    st.plotly_chart(fig_media)
else:
    st.write("No se encontró ningún reporte de vacunas privadas.")
