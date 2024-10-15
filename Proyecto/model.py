from gurobipy import GRB, Model, quicksum

#Creación de modelo
#model = Model()

#Conjuntos

#E = range(1, 4)  # Equipos
#S = range(1, 11)  # Sitios
#D = range(1, 6)  # Tipos de desastre
#TH = range(24)  # Horas del día
#TD = range(1, 8)  # Días de la semana
#TS = range(1, 5)  # Semanas del mes

#Parámetros (Todavía sin datos para usar panda, por mientras esto)

#CD = {(e, d): 1 for e in E for d in D}  # Costo fijo de despliegue
#CH = {(e, td): 1 for e in E for td in TD}  # Costo por hora de trabajo
#CO = {(s, d): 1 for s in S for d in D}  # Costo de oportunidad
#TR = {(e, d): 1 for e in E for d in D}  # Tiempo de reparación
#EP = {(e, d): 1 for e in E for d in D}  # Capacidad del equipo
#SD = {(s, d): 1 for s in S for d in D}  # Daño en el sitio
#CT = {e: 1 for e in E}  # Costo de transporte
#TCO = {(s, d): 1 for s in S for d in D}  # Tiempo de costo de oportunidad
#TM = {(s, d): 1 for s in S for d in D}  # Tiempo máximo

#Variables

#X = model.addVars (E, S, TH, TD, TS, vtype = GRB.BINARY, name = "X")
#U = model.addVars (E, S, TH, TD, TS, vtype = GRB.BINARY, name = "U")
#Z = model.addVars (E, TD, TS, vtype = GRB.BINARY, name = "Z")
#B = model.addVars (E, S, vtype = GRB.BINARY, name = "B")
#TU = model.addVars (E, S, TD, TS, vtype = GRB.INTEGER, name = "TU")
#TM = model.addVars (S, vtype = GRB.INTEGER, name = "TM")

#Para una nueva restricción 5, "Indica cuántas horas consecutivas ha estado trabajando el equipo ( e ) en el sitio ( s ) en la hora ( th ) del día ( td ) en la semana ( ts )."
#H = model.addVars(E, S, TH, TD, TS, vtype=GRB.INTEGER, name="H")

#Restricciones:

#1. Un equipo de reparación no puede estar en más de un sitio a la vez.
#model.addConstrs((quicksum(X[e, s, th, td, ts] for s in S for td in TD for ts in TS) <= 1 
                  #for e in E for th in TH), name="R1")

#2. Tiempo th en el que el equipo e comienza su trabajo de reparaci´on en el sitio s en el d´ıa td en la semana ts.
#model.addConstrs((TU[e, s, td, ts] == quicksum(th * U[e, s, th, td, ts] for th in TH) 
                  #for e in E for s in S for td in TD for ts in TS), name="R2")
#3. Un equipo tiene que esperar m´ınimo 16 horas para volver a trabajar.
#model.addConstrs((24 - (TU[e, s, td-1, ts] + TR[e, s] * Z[e, td-1, ts]) + TU[e, s, td, ts] >= 16 * Z[e, td, ts] 
                  #for e in E for s in S for td in TD for ts in TS), name="R3")
#4. Un equipo solo puede reparar un da˜no por desastre si es que est´a facultado para ello.
#model.addConstrs((quicksum(EP[e, d] * SD[s, d] for d in D) >= B[e, s] 
                  #for e in E for s in S), name="R4")

#5. Si un equipo comienza una tarea, debe completarla trabajando el total de horas necesarias.
#model.addConstrs((quicksum(X[e, s, th, td, ts] for th in range(TU[e, s, td, ts], TU[e, s, td, ts] + TR[e, s])) == TR[e, s] * quicksum(U[e, s, th, td, ts] for th in TH) 
                  #for e in E for s in S for td in TD for ts in TS), name="R5")

#Posible reemplazo
#Es larga y considera la restricción alrededor de H, debe mejorarse:
#model.addConstrs((H[e, s, th, td, ts] <= TR[e, s] for e in E for s in S for th in TH for td in TD for ts in TS), name="R5a") #H no puede pasar TR
#model.addConstrs((H[e, s, th, td, ts] == H[e, s, th-1, td, ts] + X[e, s, th, td, ts] for e in E for s in S for th in TH if th > 0 for td in TD for ts in TS), name="R5b") # H(t+1) = H(t) + X(t)
#model.addConstrs((H[e, s, 0, td, ts] == X[e, s, 0, td, ts] for e in E for s in S for td in TD for ts in TS), name="R5c") #Supuestamente H está activo durante todo el día y aumenta solo cuando se esté trabajando
#model.addConstrs((H[e, s, th, td, ts] >= TR[e, s] * U[e, s, th, td, ts] for e in E for s in S for th in TH for td in TD for ts in TS), name="R5d") #El reemplazo al original

#6. Los turnos por equipo son de m´aximo 10 horas.
#model.addConstrs((quicksum(X[e, s, th, td, ts] for s in S for th in TH) <= 10 
                  #for e in E for td in TD for ts in TS), name="R6")

#7. Un equipo debe trabajar un turno de corrido.
#model.addConstrs((TU[e, s, td, ts] + TR[e, s] - TU[e, s_prime, td, ts] - M * (1 - quicksum(U[e, s_prime, th, td, ts] for th in TH)) + 1 <= 10 
                  #for e in E for s in S for s_prime in S if s != s_prime for td in TD for ts in TS), name="R7")

#8. Un equipo puede trabajar m´aximo 44 horas semanales.
#model.addConstrs((quicksum(X[e, s, th, td, ts] for s in S for th in TH for td in TD) <= 44 
                  #for e in E for ts in TS), name="R8")

#9. Un equipo puede trabajar m´aximo 6 d´ıas a la semana y m´aximo 5 si trabaj´o el domingo.
#model.addConstrs((quicksum(Z[e, td, ts] for td in TD) <= 6 - Z[e, 7, ts] 
                  #for e in E for ts in TS), name="R9")

#10. Cada sitio con da˜no asociado a desastre debe repararse. Solo un (1) equipo trabaja por sitio.
#model.addConstrs((quicksum(U[e, s, th, td, ts] for e in E for th in TH for td in TD for ts in TS) == 1 
                  #for s in S), name="R10")

#11. La hora de inicio mas las horas de reparaci´on no pueden pasarse del d´ıa.
#model.addConstrs((TU[e, s, td, ts] + TR[e, s] <= 24 
                  #for e in E for s in S for td in TD for ts in TS), name="R11")

#12. Si el equipo e comienza a trabajar en la hora th, este no puede haber trabajado en la hora anterior.
#model.addConstrs((U[e, s, th, td, ts] >= X[e, s, th, td, ts] - X[e, s, th-1, td, ts] 
                  #for e in E for s in S for th in TH if th > 0 for td in TD for ts in TS), name="R12")

#13. Si el equipo e comienza a trabajar en una hora th, debe estar trabajando en esa hora th.
#model.addConstrs((U[e, s, th, td, ts] <= X[e, s, th, td, ts] 
                  #for e in E for s in S for th in TH for td in TD for ts in TS), name="R13")

#14. Tiempo transcurrido desde que se produjo el da˜no por desastre hasta que alg´un equipo lo repara.
#model.addConstrs((TM[s] == quicksum((24 * 7 * (ts - 1) + 24 * (td - 1) + th + TR[e, d]) * U[e, s, th, td, ts] for e in E for th in TH for td in TD for ts in TS) 
                  #for s in S), name="R14")

#Función Objetivo

#objectivo = quicksum(CO[s, d] * (TM[s, d] - TCO[s, d]) for s in S for d in D) + \
            #quicksum(CD[e, d] * B[e, s] for s in S for d in D for e in E) + \
            #quicksum(CH[e, td] * X[e, s, th, td, ts] for ts in TS for td in TD for th in TH for s in S for e in E)

#model.setObjective(objectivo, GRB.MINIMIZE)
