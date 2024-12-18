# NO TOCAR SIN PREGUNTARME (FELIPE)

import pandas as pd
# import random (si queremos añadir ruido)
# random.seed(0)

def get_data(csv_type):

    if csv_type == "real":
        
        #BASE DE DATOS REAL
        cos_opor = pd.read_csv(
        'source/real/r_costo_oportunidad.csv', header=None)
        cos_despl = pd.read_csv(
        'source/real/r_costos_por_despliegue.csv', header=None)
        cos_hor = pd.read_csv(
        'source/real/r_costos_por_hora.csv', header=None)
        hor_arreg = pd.read_csv(
        'source/real/r_horas_arreglo.csv', header=None)
        pue_encarg = pd.read_csv(
        'source/real/r_puede_encargarse.csv', header=None)
    
    elif csv_type == "small":
        
        #BASE DE DATOS PEQUEÑA
        cos_opor = pd.read_csv(
        'source/small/costo_oportunidad.csv', header=None)
        cos_despl = pd.read_csv(
        'source/small/costos_por_despliegue.csv', header=None)
        cos_hor = pd.read_csv(
        'source/small/costos_por_hora.csv', header=None)
        hor_arreg = pd.read_csv(
        'source/small/horas_arreglo.csv', header=None)
        pue_encarg = pd.read_csv(
        'source/small/puede_encargarse.csv', header=None)
        
    #elif OTRA BASE
    #elif OTRA BASE


    # COMPARTIDO
  
    # Crear conjuntos
  
    E = list(range(len(cos_despl.columns))) #columnas de .csv son equipos
    S = list(range(len(cos_despl))) #filas de .csv son sitios
    TH = list(range(336))
    TD = list(range(7))
    TS = list(range(2))
  
    # Crear parámetros

    CO_s = {i: int(cos_opor.iat[i, 0]) for i in S}
    CD_es = {(i, j): int(cos_despl.iat[i, j]) for i in S for j in E}
    CH_e = {j: int(cos_hor.iat[0, j]) for j in E}
    TR_es = {(i, j): int(hor_arreg.iat[i, j]) for i in S for j in E}
    EP_es = {(i, j): int(pue_encarg.iat[i, j]) for i in S for j in E}

    # Exporta los conjuntos

    return E, S, TH, TD, TS, CO_s, CD_es, CH_e, TR_es, EP_es










