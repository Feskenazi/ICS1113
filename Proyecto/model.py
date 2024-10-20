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

    X_e_s_th = model.addVars(E, S, TH, vtype=GRB.BINARY, name="X_e_s_th")
    U_e_s_th = model.addVars(E, S, TH, vtype=GRB.BINARY, name="U_e_s_th")
    TU_e_s_th = model.addVars(E, S, TH, vtype=GRB.INTEGER, name="TU_e_s_th")
    TM_s = model.addVars(S, vtype=GRB.INTEGER, name="TM_s")
    Z_e_td_ts = model.addVars(E, TD, TS, vtype=GRB.INTEGER, name="Z_e_td_ts")
    HW_e_th = model.addVars(E, TH, vtype=GRB.INTEGER, name="HW_e_th")
    HD_e_th = model.addVars(E, TH, vtype=GRB.INTEGER, name="HD_e_th")
    

    # Restricciones

    # Función objetivo

    # Optimizar
    model.optimize()

    # Conformación del archivo solución si es factible/óptimo

    return None





