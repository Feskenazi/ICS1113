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
      

    
    



