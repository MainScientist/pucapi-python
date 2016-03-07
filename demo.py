from pucapi import login


alumno = login("user", "password")
print(alumno.pga)
for semestre in alumno.ficha_academica.semestres:
    print(semestre.periodo)
    for ramo in semestre.ramos_cursados:
        print(ramo.nombre, ramo.sigla, ramo.nota)
print(alumno.buscar_persona_simple("FELIPE IGNACIO PEZOA"))
