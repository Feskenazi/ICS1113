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

    # 1. Un equipo de reparación no puede estar en más de un sitio a la vez
    for e in E:
        for th in TH:
            model.addConstr(gp.quicksum(X_e_s_th[e, s, th] for s in S) <= 1, name="R1")

    # 2. Un equipo descansará cuando no esté trabajando en ningún sitio durante una hora, debe descansar mínimo 16 horas antes de volver a trabajar
    for e in E:
        for th in range(1, len(TH)):
            model.addConstr(HD_e_th[e, th] >= HD_e_th[e, th-1] + 1 - 672 * gp.quicksum(X_e_s_th[e, s, th] for s in S), name="R2a")
            model.addConstr(HD_e_th[e, th] <= HD_e_th[e, th-1] + 1 - gp.quicksum(X_e_s_th[e, s, th] for s in S), name="R2b")
        model.addConstr(HD_e_th[e, 0] == 1 - gp.quicksum(X_e_s_th[e, s, 0] for s in S), name="R2c")
        for th in range(1, len(TH)):
            model.addConstr(HD_e_th[e, th-1] >= 16 * gp.quicksum(U_e_s_th[e, s, th] for s in S), name="R2d")

    # 3. Si un equipo estará trabajando si repara al menos un sitio en una hora, las horas de trabajo seguidas de un equipo debe ser máximo 10 horas
    for e in E:
        for th in range(1, len(TH)):
            model.addConstr(HW_e_th[e, th] >= HW_e_th[e, th-1] + 1 + 11 * gp.quicksum(X_e_s_th[e, s, th] for s in S) - 1, name="R3a")
            model.addConstr(HW_e_th[e, th] <= HW_e_th[e, th-1] + 1 + gp.quicksum(X_e_s_th[e, s, th] for s in S) - 1, name="R3b")
        model.addConstr(HW_e_th[e, 0] == gp.quicksum(X_e_s_th[e, s, 0] for s in S), name="R3c")
        for th in TH:
            model.addConstr(HD_e_th[e, th-1] <= 10 * gp.quicksum(X_e_s_th[e, s, th] for s in S), name="R3d")

    # 4. Tiempo acumulado en horas que un equipo ha estado trabajando en un sitio
    for e in E:
        for s in S:
            for th in range(1, len(TH)):
                model.addConstr(TU_e_s_th[e, s, th] >= TU_e_s_th[e, s, th-1] + 1 + 11 * gp.quicksum(X_e_s_th[e, s, th] for s in S) - 1, name="R4a")
                model.addConstr(TU_e_s_th[e, s, th] <= TU_e_s_th[e, s, th-1] + 1 + 1 - gp.quicksum(X_e_s_th[e, s, th] for s in S), name="R4b")
            model.addConstr(TU_e_s_th[e, s, 0] == gp.quicksum(X_e_s_th[e, s, 0] for s in S), name="R4c")

    # 5. Un equipo debe haber terminado la reparación de un sitio sin detenerse una vez empezado
    for e in E:
        for s in S:
            for th in TH:
                model.addConstr(TU_e_s_th[e, s, th] <= TR_es[e, s], name="R5a")
            for th in range(len(TH) - TR_es[e, s]):
                model.addConstr(U_e_s_th[e, s, th] * TR_es[e, s] == TU_e_s_th[e, s, th + TR_es[e, s] - 1], name="R5b")

    # 6. Cada sitio con daño asociado a desastre debe repararse. Solo un equipo trabaja por sitio
    for s in S:
        model.addConstr(gp.quicksum(U_e_s_th[e, s, th] for e in E for th in TH) == 1, name="R6")

    # 7. Si el equipo e comienza a trabajar en la hora th en un sitio s, este no puede haber trabajado en este mismo durante la hora anterior
    for e in E:
        for s in S:
            for th in range(1, len(TH)):
                model.addConstr(U_e_s_th[e, s, th] >= X_e_s_th[e, s, th] - X_e_s_th[e, s, th-1], name="R7a")
                model.addConstr(U_e_s_th[e, s, th] <= 1 - X_e_s_th[e, s, th-1], name="R7b")
            model.addConstr(U_e_s_th[e, s, 0] <= X_e_s_th[e, s, 0] - X_e_s_th[e, s, len(TH)-1], name="R7c")

    # 8. Si el equipo e comienza a trabajar en una hora th, debe estar trabajando en esa hora th
    for e in E:
        for s in S:
            for th in TH:
                model.addConstr(U_e_s_th[e, s, th] <= X_e_s_th[e, s, th], name="R8")

    # 9. Tiempo transcurrido desde que se produjo el daño por desastre hasta que algún equipo lo repara
    for s in S:
        model.addConstr(TM_s[s] == gp.quicksum(th * U_e_s_th[e, s, th] for e in E for th in TH), name="R9")

    # 10. Un equipo solo puede reparar los daños de un sitio si está facultado para ello
    for e in E:
        for s in S:
            model.addConstr(gp.quicksum(U_e_s_th[e, s, th] for th in TH) <= EP_es[e, s], name="R10")

    # 11. Un equipo puede trabajar máximo 44 horas semanales
    for e in E:
        for ts in TS:
            model.addConstr(gp.quicksum(X_e_s_th[e, s, th] for s in S for th in range(ts * 168, (ts + 1) * 168)) <= 44, name="R11")

    # 12. Se deben tener 2 días de descanso a la semana al haber trabajado los otros 5
    for e in E:
        for ts in TS:
            model.addConstr(gp.quicksum(Z_e_td_ts[e, td, ts] for td in TD) <= 6 - Z_e_td_ts[e, 7, ts], name="R12")

    # 13. Se habrá trabajado en un día td de una semana ts si se ha trabajado al menos una vez durante una hora th de dicho día
    for e in E:
        for ts in TS:
            for td in TD:
                model.addConstr(gp.quicksum(X_e_s_th[e, s, k] for s in S for k in range(td * 24 + ts * 168, (td + 1) * 24 + ts * 168)) <= 24 * Z_e_td_ts[e, td, ts], name="R13a")
                model.addConstr(gp.quicksum(X_e_s_th[e, s, k] for s in S for k in range(td * 24 + ts * 168, (td + 1) * 24 + ts * 168)) >= Z_e_td_ts[e, td, ts], name="R13b")

    # Función objetivo
    model.setObjective(
    gp.quicksum(CO_s[s] * TM_s[s] for s in S) +
    gp.quicksum(CD_es[e, s] * U_e_s_th[e, s, th] for e in E for s in S for th in TH) +
    gp.quicksum(CH_e[e] * X_e_s_th[e, s, th] for e in E for s in S for th in TH),
    GRB.MINIMIZE
    )

    # Función objetivo

    # Optimizar
    model.optimize()

    # Conformación del archivo solución si es factible/óptimo

    return None





