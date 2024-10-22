# IMPORTAR
from parameters import get_data
from model import generate_model

if __name__ == '__main__':
    
    print("Proyecto grupo 72")
    print("Elegir la base de datos a utilizar: small o real") # 2, 3 o 4 bases de datos
    
    base_datos = input("Introducir la base de datos que se quiere utilizar: ")
    
    if base_datos == "real":
        parameters = get_data("real")
  
    elif base_datos == "small":
        parameters = get_data("small")

    else:
        print("Base de datos introducida no encontrada")
        exit()
    
    generate_model(parameters)


  
  
