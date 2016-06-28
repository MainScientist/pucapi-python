class Ramo:

    def __init__(self, nombre, nrc, creditos, seccion, profesores, sigla="", requisitos="",
                 programa="", cupos_totales=0, cupos_disponibles=0, campus="", unidad_academica="",
                 categoria="", modulos=None, retirable=False, en_ingles=False, aprob_especial=False):
        self.nombre = nombre
        self.creditos = creditos
        self.sigla = sigla
        self.requisitos = requisitos  # Class
        self.nrc = nrc
        self.seccion = seccion
        self.profesores = profesores
        self.programa = programa
        self.cupos_totales = cupos_totales  # Make class
        self.cupos_disponibles = cupos_disponibles  # Make class
        self.campus = campus
        self.modulos = modulos if modulos else []
        for m in self.modulos:
            m.ramo = self
        self.unidad_academica = unidad_academica
        self.categoria = categoria
        self.retirable = retirable
        self.en_ingles = en_ingles
        self.aprob_especial = aprob_especial

    @property
    def horario(self):
        s = ""
        horarios = {}
        for modulo in self.modulos:
            if modulo.tipo not in horarios:
                horarios[modulo.tipo] = {modulo.dia: [modulo.numero]}
            else:
                if modulo.dia not in horarios[modulo.tipo]:
                    horarios[modulo.tipo][modulo.dia] = [modulo.numero]
                else:
                    horarios[modulo.tipo][modulo.dia].append(modulo.numero)
        return horarios

    def topa(self, otro_ramo):
        topan = [modulo for modulo in self.modulos for otro_modulo in otro_ramo.modulos if modulo.topa(otro_modulo)]
        if len(topan) > 0:
            return True
        return False

    def tiene_requisitos(self):
        return self.requisitos is not None

    def alumno_cumple_requisitos(self, alumno_uc):
        if self.tiene_requisitos():
            return self.requisitos.cumple_requisito(alumno_uc.ramos_cursados)
        else:
            return True

    def __repr__(self):
        return self.sigla + "-" + str(self.seccion) + "({})".format(self.nombre)
