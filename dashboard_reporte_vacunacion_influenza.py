# Importar librerías
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Función para leer el último archivo creado con el nombre Reporte_vacunas en la carpeta "Reporte"
def leer_ultimo_Reporte_vacunas(directorio):
    # Buscar todos los archivos en el directorio que contengan "Reporte_vacunas"
    archivos = [os.path.join(directorio, f) for f in os.listdir(directorio) if "Reporte_vacunas" in f and f.endswith(".csv")]
    
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

# Leer el último reporte de vacunas publica
ultimo_reporte, fecha_creacion = leer_ultimo_Reporte_vacunas(directorio_reporte)
ultimo_reporte = ultimo_reporte.loc[~(ultimo_reporte['SERVICIO'] == 'SEREMI Metropolitana de Santiago')]
ultimo_reporte = ultimo_reporte.loc[~(ultimo_reporte['SERVICIO'] == 'Ministerio de Salud')]

# Mostrar el DataFrame en Streamlit si se encuentra un archivo
if ultimo_reporte is not None:
    st.title("Reporte de Vacunaciones pública")
    st.write(f"Último Reporte de Vacunas pública (Creado el {fecha_creacion.strftime('%Y-%m-%d')}):")
    st.write("Nota: El separador de miles es '.' y el separador decimal es ','. Este reporte fue generado por el Subdepartamento de gestión de la información y estadística de la Seremi de Salud de la Región Metropolitana.")
    
    # Seleccionar comunas
    todas_comunas = ["Todas las comunas"] + sorted(list(ultimo_reporte['COMUNA_OCURR'].unique()))
    comunas_seleccionadas = st.multiselect("Seleccione las comunas para mostrar:", options=todas_comunas, default="Todas las comunas")
    
    # Filtrar el DataFrame según las comunas seleccionadas
    if "Todas las comunas" in comunas_seleccionadas:
        reporte_filtrado = ultimo_reporte
    else:
        reporte_filtrado = ultimo_reporte[ultimo_reporte['COMUNA_OCURR'].isin(comunas_seleccionadas)]
    
    # Formatear los números
    reporte_filtrado = reporte_filtrado.applymap(lambda x: f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(reporte_filtrado.reset_index(drop=True))

    # Agrupar por comuna y sumar las vacunaciones
    suma_por_comuna = reporte_filtrado.groupby('COMUNA_OCURR').agg(
        vacunacion_ultimos_3_dias=('vacunacion_ultimos_3_dias', 'sum'),
        vacunacion_ultimos_7_dias=('vacunacion_ultimos_7_dias', 'sum'),
        vacunacion_ultimos_14_dias=('vacunacion_ultimos_14_dias', 'sum')
    ).reset_index()

    # Calcular los promedios por día
    suma_por_comuna['promedio_por_dia_3'] = suma_por_comuna['vacunacion_ultimos_3_dias'] / 3
    suma_por_comuna['promedio_por_dia_7'] = suma_por_comuna['vacunacion_ultimos_7_dias'] / 7
    suma_por_comuna['promedio_por_dia_14'] = suma_por_comuna['vacunacion_ultimos_14_dias'] / 14

    # Formatear los números
    suma_por_comuna = suma_por_comuna.applymap(lambda x: f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.subheader("Suma de Vacunaciones por Comuna")
    st.dataframe(suma_por_comuna)

    st.subheader("Promedio de Vacunaciones por Día y por Comuna")
    st.dataframe(suma_por_comuna[['COMUNA_OCURR', 'promedio_por_dia_3', 'promedio_por_dia_7', 'promedio_por_dia_14']])
else:
    st.write("No se encontró ningún reporte de vacunas pública.")
