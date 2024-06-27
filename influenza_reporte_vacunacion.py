#%%
# Importar librerias
import pandas as pd
import os
from datetime import datetime, timedelta
#%%
# Definición de funciones
##  Funcion de vacuna 
def rni_filtros(df):
    criterio_elegibilidad = ['EPRO', 'Casos especiales']
    df1 = df.loc[df['VACUNA_ADMINISTRADA'] == "SI"]
    df2 = df1.loc[df1['REGISTRO_ELIMINADO'] == "NO"]
    df3 = df2.loc[~(df2['CRITERIO_ELEGIBILIDAD'].isin(criterio_elegibilidad))]
    df4 = df3.loc[~(df3['DOSIS'] == 'EPRO')]
    return df4
## Funcion para definir tipo de lote
def tipo_lote(df):
    df['LOTE']=df['LOTE'].astype(str)
    df['TIPO_LOTE'] = df['LOTE'].apply(lambda x: 'Privado' if 'privado' in x.lower() else 'Ministerial')
    return df
## Función para agregar columnas de vacunación en los últimos días
def agregar_vacunacion_dias(df, dias):
    hoy = datetime.today()
    rango_fecha_inicio = hoy - timedelta(days=dias+1)
    columna_nombre = f'vacunacion_ultimos_{dias}_dias'
    df[columna_nombre] = df['FECHA_INMUNIZACION'].apply(
        lambda x: 1 if rango_fecha_inicio <= datetime.strptime(x, '%Y-%m-%d') <= hoy else 0
    )
    return df
#%%
# Lectura de columnas y de influenza

## Directorio raíz donde se encuentran los archivos CSV
directorio_raiz_influ = r'C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\PNI\DATA\Influenza 2024\OCU'
lista_archivos_influ = []

## Buscar archivos CSV en el directorio raíz y subdirectorios
for raiz, dirs, archivos in os.walk(directorio_raiz_influ):
    for archivo in archivos:
        if archivo.endswith('.csv'):
            ruta_completa = os.path.join(raiz, archivo)
            lista_archivos_influ.append(ruta_completa)

## Lectura de columnas de influenza
# path_file= r'C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\PNI\DATA\Influenza 2024\Influenza2024_0.csv'
# col=pd.read_csv(path_file,nrows=1,sep='|',encoding='LATIN1',low_memory=False).columns
#%%
# Lectura de archivos y definicion de columnas a utilizar 
## Columnas a utilizar
cols=[
    'ID_INMUNIZACION', # ID unico
    'COD_REGION', # 'COD_REGION' == '13'
    'COMUNA_OCURR', # identificar la comuna
    'ESTABLECIMIENTO', # Identificacion del vacunatorio
    'CODIGO_DEIS', # Para cruzar con Establecimientos DEIS MINSAL
    'SERVICIO', # Si es de SS respectivo o SEREMI 
    'LOTE', # Identificar lote Ministerial
    'FECHA_INMUNIZACION', # Se utiliza para establecer tiempos
    'DOSIS', # Filtro 'DOSIS' != 'EPRO'
    'VACUNA_ADMINISTRADA', # Filtro 'VACUNA_ADMINISTRADA' == 'SI'
    'REGISTRO_ELIMINADO', # Filtro 'REGISTRO_ELIMINADO' == 'NO'
    'CRITERIO_ELEGIBILIDAD', # Filtro 'CRITERIO_ELEGIBILIDAD' distinto a ['EPRO', 'Casos especiales']
]

lista_df=[]

## Leer y agregar cada archivo CSV a una lista de DataFrames
for archivo in lista_archivos_influ:
    df = pd.read_csv(archivo, encoding='LATIN1', sep='|', usecols=cols, low_memory=False)
    df['source'] = archivo
    lista_df.append(df)
df_vac = pd.concat(lista_df)
#%%
# Filtros
## Aplicar filtros
df_vac_rm=df_vac.loc[df_vac.COD_REGION==13]
df_vac_rm_filter=rni_filtros(df_vac_rm)
df_vac_rm_filter_lote=tipo_lote(df_vac_rm_filter)
df_vac_rm_filter_lote_minist=df_vac_rm_filter_lote.loc[df_vac_rm_filter_lote.TIPO_LOTE=='Ministerial']
#%%
# Leer el archivo de establecimientos DEIS
df_deis = pd.read_excel("Establecimientos DEIS MINSAL 28-05-2024 (1) (1).xlsx", skiprows=1)
df_deis_dep = df_deis[['Código Vigente', 'Código Antiguo ', 'Nombre Dependencia Jerárquica (SEREMI / Servicio de Salud)']]

# Convertir los códigos a string
df_deis_dep['Código Vigente'] = df_deis_dep['Código Vigente'].astype('str')
df_deis_dep['Código Antiguo '] = df_deis_dep['Código Antiguo '].astype('str')

# Crear el diccionario con código vigente y nombre de dependencia
diccionario_dependencias = pd.Series(df_deis_dep['Nombre Dependencia Jerárquica (SEREMI / Servicio de Salud)'].values, index=df_deis_dep['Código Vigente']).to_dict()

# Agregar código antiguo al diccionario
diccionario_dependencias.update(pd.Series(df_deis_dep['Nombre Dependencia Jerárquica (SEREMI / Servicio de Salud)'].values, index=df_deis_dep['Código Antiguo ']).to_dict())
diccionario_dependencias.update({'09-407':'Servicio de Salud'})
# Convertir CODIGO_DEIS a string
df_vac_rm_filter_lote_minist['CODIGO_DEIS'] = df_vac_rm_filter_lote_minist['CODIGO_DEIS'].astype('str')

# Hacer un map en CODIGO_DEIS utilizando el diccionario
df_vac_rm_filter_lote_minist['Nombre Dependencia Jerárquica'] = df_vac_rm_filter_lote_minist['CODIGO_DEIS'].map(diccionario_dependencias)

# Identificar los establecimientos sin dependencia jerárquica
establecimientos_sin_dependencia = df_vac_rm_filter_lote_minist[df_vac_rm_filter_lote_minist['Nombre Dependencia Jerárquica'].isna()]
#%%
# %%
# Aplicar la función para los últimos 3, 7 y 14 días
df_vac_rm_filter_lote_minist = agregar_vacunacion_dias(df_vac_rm_filter_lote_minist, 3)
df_vac_rm_filter_lote_minist = agregar_vacunacion_dias(df_vac_rm_filter_lote_minist, 7)
df_vac_rm_filter_lote_minist = agregar_vacunacion_dias(df_vac_rm_filter_lote_minist, 14)

#%%
# Agrupar y sumar las vacunaciones por comuna y establecimiento
reporte_minist = df_vac_rm_filter_lote_minist.groupby(['SERVICIO','COMUNA_OCURR', 'ESTABLECIMIENTO']).agg(
    vacunacion_ultimos_3_dias=('vacunacion_ultimos_3_dias', 'sum'),
    vacunacion_ultimos_7_dias=('vacunacion_ultimos_7_dias', 'sum'),
    vacunacion_ultimos_14_dias=('vacunacion_ultimos_14_dias', 'sum')
).reset_index()

#%%
# Mostrar el reporte ministerial
print(reporte_minist)

#%%
hoy = datetime.today()
hoy_str = hoy.strftime('%Y%m%d')
nombre_archivo_minist = f'{hoy_str}_Reporte_vacunas_ministeriales.csv'
reporte_minist.to_csv(f'Reporte/{nombre_archivo_minist}', index=False)
