import pandas as pd
# import random (si queremos añadir ruido)
# random.seed(0)

def get_data(csv_type):
  
  if csv_type == "small":
    
    #BASE DE DATOS PEQUEÑA
    cos_opor = pd.read_csv(
      'source/small/costo_oportunidad.csv', header=None)
    cos_despl = pd.read_csv(
      'source/small/costos_por_despliegue.csv', header=None)
    cos_hor = pd.read_csv(
      'source/small/costos_por_hora.csv', header=None)
    des_sit = pd.read_csv(
      'source/small/desastre_del_sitio.csv', header=None)
    hor_arreg = pd.read_csv(
      'source/small/horas_arreglo.csv', header=None)
    pue_encarg = pd.read_csv(
      'source/small/puede_encargarse.csv', header=None)
        
  #elif csv_type == "real":
  #elif OTRA BASE
  #elif OTRA BASE


  # COMPARTIDO--------------------
  
  # Crear conjuntos
  
  E = list(range(len(cos_despl)))
  S = list(range(len(des_sit)))
  D = list(range(len(des_sit.columns)))
  TH = list(range(24))
  TD = list(range(7))
  TS = list(range(4))
  
  # Crear parámetros

  CO_ed = {(i, j): int(cos_opor.iat[i, j]) for i in E for j in D}
  CD_ed = {(i, j): int(cos_despl.iat[i, j]) for i in E for j in D}
  #CH ver que onda 
  SD_sd = {(i, j): int(des_sit.iat[i, j]) for i in S for j in D}


