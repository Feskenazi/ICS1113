# IMPORTAR
from parameters import get_data
from model import generate_model

if __name__ == '__main__':

  print("Proyecto grupo 72")
  print("Elegir la base de datos a utilizar: small, ..., real") # 2, 3 o 4 bases de datos
  
  base_datos = input("Introducir la base de datos que se quiere utilizar: ")

  if base_datos == "small":
  parameters = get_data("small")
  
  #elif base_datos == "x":
    #parameters = get_data("x") ...

  else:
    print("Base de datos no encontrada")
    exit()
  
  generate_model(parameters)


  
  
