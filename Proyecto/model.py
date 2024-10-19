#GUROBI
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from parameters import get_data
# from plot import plot_solution

#Generacion del modelo

def generate_model(PARAMETERS):

  #Obtener los datos desde parameters.py
  E, S, TH, TD, TS, CO_s, CD_es, CH_e, TR_es, EP_es = PARAMETERS

  model = gp.Model("Proyecto grupo 72")
  model.setParam("TimeLimit", 1800)  # tiempo max de ejecución 30 minutos

  # Variables

  # Restricciones

  # Función objetivo

  # Optimizar
  model.optimize

  # Conformación del archivo solución si es factible/óptimo

  return None





