import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from parameters import get_data
import os

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
            #model.addConstr(HD_e_th[e,th] <= 16 * (1 - gp.quicksum(X_e_s_th[e, s, th] for s in S)))
        model.addConstr(HD_e_th[e, 0] == 1 - gp.quicksum(X_e_s_th[e, s, 0] for s in S), name="R2c")
        for th in range(9, len(TH)):
            model.addConstr(HD_e_th[e, th-1] >= 16 * gp.quicksum(U_e_s_th[e, s, th] for s in S), name="R2d")

    # 3. Si un equipo estará trabajando si repara al menos un sitio en una hora, las horas de trabajo seguidas de un equipo debe ser máximo 10 horas
    for e in E:
        for th in range(1, len(TH)):
            model.addConstr(HW_e_th[e, th] >= HW_e_th[e, th-1] + 1 + 11 * (gp.quicksum(X_e_s_th[e, s, th] for s in S) - 1), name="R3a")
            model.addConstr(HW_e_th[e, th] <= HW_e_th[e, th-1] + 1 + gp.quicksum(X_e_s_th[e, s, th] for s in S) - 1, name="R3b")
        model.addConstr(HW_e_th[e, 0] == gp.quicksum(X_e_s_th[e, s, 0] for s in S), name="R3c")
        for th in TH:
            model.addConstr(HW_e_th[e, th] <= 10 * gp.quicksum(X_e_s_th[e, s, th] for s in S), name="R3d")

    # 4. Tiempo acumulado en horas que un equipo ha estado trabajando en un sitio
    for e in E:
        for s in S:
            for th in range(1, len(TH)):
                model.addConstr(TU_e_s_th[e, s, th] >= TU_e_s_th[e, s, th-1] + 1 + 11 * (X_e_s_th[e, s, th] - 1), name="R4a")
                model.addConstr(TU_e_s_th[e, s, th] <= TU_e_s_th[e, s, th-1] + 1 + 1 - X_e_s_th[e, s, th], name="R4b")
                model.addConstr(TU_e_s_th[e, s, th] <= 1000 *  X_e_s_th[e, s, th])
            model.addConstr(TU_e_s_th[e, s, 0] == (X_e_s_th[e, s, 0]), name="R4c")
    # 5. Un equipo debe haber terminado la reparación de un sitio sin detenerse una vez empezado
    for e in E:
        for s in S:
            for th in TH:
                model.addConstr(TU_e_s_th[e, s, th] <= TR_es[s, e], name="R5a")
            for th in range(0, len(TH) - TR_es[s, e]):
                model.addConstr(U_e_s_th[e, s, th] * TR_es[s, e] <= TU_e_s_th[e, s, th + TR_es[s, e] - 1])
            for th in range(0, len(TH) - TR_es[s, e]):
                model.addConstr(1000*(1 - U_e_s_th[e, s, th]) * TR_es[s, e] + U_e_s_th[e, s, th] * TR_es[s, e] >= TU_e_s_th[e, s, th + TR_es[s, e] - 1])
                
            #for th in range(len(TH) - TR_es[s, e] + 1):
             #   model.addConstr(gp.quicksum(X_e_s_th[e, s, th] for th in range(th, th + TR_es[s, e] -1)) >= U_e_s_th[e, s, th] * TR_es[e, s] , name="R5B")
            #for th in range(len(TH) - TR_es[s, e] + 1 ):
             #   model.addConstr(gp.quicksum(X_e_s_th[e, s, th] for th in range(th, th + TR_es[s, e] -1)) <= U_e_s_th[e, s, th] * TR_es[e, s] +  1000 * (1 - U_e_s_th[e, s, th]), name="R5B")
                
            #for th in range(len(TH) - TR_es[s, e] -1):
             #   model.addConstr(U_e_s_th[e, s, th] * TR_es[e, s] <= TU_e_s_th[e, s, th + TR_es[e, s] - 1])
            #for th in range(len(TH) - TR_es[s, e] - 1):
             #   model.addConstr(1000*(1 - U_e_s_th[e, s, th]) * TR_es[e, s] + U_e_s_th[e, s, th] * TR_es[e, s] >= TU_e_s_th[e, s, th + TR_es[e, s] - 1])
            #for th in range(len(TH) - TR_es[s, e]):
             #   model.addConstr(U_e_s_th[e, s, th] * TR_es[s, e] == TU_e_s_th[e, s, th + TR_es[s, e] -1 ], name="R5b")
           # for th in range(len(TH) - TR_es[s, e] + 1):
            #    model.addConstr(gp.quicksum(X_e_s_th[e, s, th] for th in range(th, th + TR_es[s, e] -1)) >= U_e_s_th[e, s, th] * TR_es[e, s] , name="R5B")
          #  for th in range(len(TH) - TR_es[s, e] + 1 ):
           #     model.addConstr(gp.quicksum(X_e_s_th[e, s, th] for th in range(th, th + TR_es[s, e] -1)) <= U_e_s_th[e, s, th] * TR_es[e, s] +  1000 * (1 - U_e_s_th[e, s, th]), name="R5B")
              #  model.addConstr(X_e_s_th[e,s,th] <= U_e_s_th[e,s,th] * TR_es[s, e])

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
        model.addConstr(TM_s[s] == gp.quicksum((th + TR_es[s,e]) * U_e_s_th[e, s, th] for e in E for th in TH), name="R9")

    # 10. Un equipo solo puede reparar los daños de un sitio si está facultado para ello
    for e in E:
        for s in S:
            model.addConstr(gp.quicksum(U_e_s_th[e, s, th] for th in TH) <= EP_es[s, e], name="R10")

    # 11. Un equipo puede trabajar máximo 44 horas semanales
    for e in E:
        for ts in TS:
            model.addConstr(gp.quicksum(X_e_s_th[e, s, th] for s in S for th in range(ts * 168, (ts + 1) * 168)) <= 44, name="R11")

    # 12. Se deben tener 2 días de descanso a la semana al haber trabajado los otros 5
    for e in E:
        for ts in TS:
            model.addConstr(gp.quicksum(Z_e_td_ts[e, td, ts] for td in TD) <= 6 - Z_e_td_ts[e, 6, ts], name="R12")

    # 13. Se habrá trabajado en un día td de una semana ts si se ha trabajado al menos una vez durante una hora th de dicho día
    for e in E:
        for ts in TS:
            for td in TD:
                model.addConstr(gp.quicksum(X_e_s_th[e, s, k] for s in S for k in range(td * 24 + ts * 168, (td + 1) * 24 + ts * 168)) <= 24 * Z_e_td_ts[e, td, ts], name="R13a")
                model.addConstr(gp.quicksum(X_e_s_th[e, s, k] for s in S for k in range(td * 24 + ts * 168, (td + 1) * 24 + ts * 168)) >= Z_e_td_ts[e, td, ts], name="R13b")

    # Función objetivo
    model.setObjective(
    gp.quicksum(CO_s[s] * TM_s[s] for s in S) +
    gp.quicksum(CD_es[s, e] * U_e_s_th[e, s, th] for e in E for s in S for th in TH) +
    gp.quicksum(CH_e[e] * X_e_s_th[e, s, th] for e in E for s in S for th in TH),
    GRB.MINIMIZE
    )

    # Optimizar
    model.optimize()

    # Conformación del archivo solución

    if os.path.exists("output/resultado.txt"):
        os.remove("output/resultado.txt")

    if os.path.exists("output/model.ilp"):
        os.remove("output/model.ilp")
    
    if os.path.exists("output/infeasibility_report.txt"):
        os.remove("output/infeasibility_report.txt")

    if model.status == GRB.INFEASIBLE:
        print("El modelo es infactible. Diagnosticando")
        model.computeIIS()
        model.write("output/model.ilp")

        with open("output/infeasibility_report.txt", "w") as f:
            f.write("IIS Report:\n")
            for c in model.getConstrs():
                if c.IISConstr:
                    f.write(f"{c.constrName}\n")

    else:
        if model.status == GRB.OPTIMAL:
            #for s in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]:
                #print(f"----------------Sitio {s}----------------")
                #for th in range(60):
                 #   print(f"------Hora {th}--------")
                  #  print(f"TU Equipo 0: {TU_e_s_th[0, s, th].X}")
                   # print(f"U Equipo 0: {U_e_s_th[0, s, th].X}")
                    #print(f"X Equipo 0: {X_e_s_th[0, s, th].X}")
            print("Solución óptima encontrada.")
            lista = []
            for e in E:
                for s in S:
                    for th in TH:
                        if U_e_s_th[e, s, th].X == 1:
                            lista.append(f"El equipo {e} comienza a trabajar en el sitio {s} en la hora {th}.")
    
            lista.append(f"Valor objetivo: {model.objVal}")
            lista.append(f"Tiempo de ejecución: {model.Runtime}")
            archivo = open("output/resultado.txt", "w")

            for l in lista:
                archivo.write(l + "\n")
            archivo.close()

        else:
            print("No se encontró solución óptima o existe un problema con el modelo.")
            print(f"Tiempo de ejecución: {model.Runtime}")
            lista = []
            for e in E:
                for s in S:
                    for th in TH:
                        if U_e_s_th[e, s, th].X > 0.5:
                            lista.append(f"El equipo {e} comienza a trabajar en el sitio {s} en la hora {th}.")
    
            lista.append(f"Valor objetivo: {model.objVal}")
            lista.append(f"Tiempo de ejecución: {model.Runtime}")
            archivo = open("output/resultado.txt", "w")

            for l in lista:
                archivo.write(l + "\n")
            archivo.close()

        

    return None


    return None

