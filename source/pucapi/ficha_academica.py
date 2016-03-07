import requests
from bs4 import BeautifulSoup


class FichaAcademica:

    def __init__(self, alumno):
        self.alumno = alumno
        self.semestres = []
        self.cargar_datos()

    def cargar_datos(self):
        session = requests.session()
        session.get("https://ssb.uc.cl/ERPUC/twbkwbis.P_WWWLogin")
        session.post("https://ssb.uc.cl/ERPUC/twbkwbis.P_ValLogin", data={"sid": self.alumno.username,
                                                                          "PIN": self.alumno.password})
        ficha_request = session.post("https://ssb.uc.cl/ERPUC/bwskotrn.P_ViewTran", {"levl": "", "tprt": "FAA"})
        
        ficha_page = BeautifulSoup(ficha_request.content.decode("UTF-8"), "html.parser")
        trs = ficha_page.find_all("tr")
        semestre = None
        for tr in trs:
            th = tr.find("th")
            if th is not None:
                if "class" in th.attrs and "ddlabel" in th.attrs["class"] and "colspan" in \
                        th.attrs:
                    if th.attrs["colspan"] == "12" or th.attrs["colspan"] == "11":
                        if semestre is not None and semestre not in self.semestres:
                            self.semestres.append(semestre)
                        first_space = th.text.find(" ")
                        second_space = th.text.find(" ", first_space + 1)
                        third_space = th.text.find(" ", second_space + 1)
                        year = th.text[first_space + 1:second_space]
                        sem = th.text[second_space+1:third_space]
                        if sem == "Primer":
                            periodo = year + "-1"
                        else:
                            periodo = year + "-2"
                        semestre = self.buscar_semestre(periodo)
                        if semestre is None:
                            semestre = Semestre(self, periodo)
            tds = tr.find_all("td", {"class": "dddefault"})
            if len(tds) > 0:
                if len(tds) == 8:
                    sigla = tds[0].text + tds[1].text
                    nombre = tds[3].text
                    nota = tds[4].text.replace(" ", "")
                    creditos = tds[5].text.replace(" ", "")
                    r = RamoCursado(sigla, nombre, nota, semestre, creditos)
                    semestre.ramos_cursados.append(r)
                elif len(tds) == 5:
                    sigla = tds[0].text + tds[1].text
                    nombre = tds[3].text
                    creditos = tds[4].text.replace(" ", "")
                    r = RamoEnCurso(sigla, nombre, semestre, creditos)
                    semestre.ramos_en_curso.append(r)
        if semestre is not None:
            self.semestres.append(semestre)

    def buscar_semestre(self, periodo):
        for semestre in self.semestres:
            if semestre.periodo == periodo:
                return semestre


class Semestre:

    def __init__(self, ficha_academica, periodo, ramos_cursados=None, ramos_en_curso=None):
        self.ficha_academica = ficha_academica
        self.periodo = periodo
        if ramos_en_curso is None:
            ramos_en_curso = []
        if ramos_cursados is None:
            ramos_cursados = []
        self.ramos_cursados = ramos_cursados
        self.ramos_en_curso = ramos_en_curso


class RamoCursado:

    def __init__(self, sigla, nombre, nota, semestre, creditos):
        self.sigla = sigla
        self.nombre = nombre
        self.nota = nota
        self.semestre = semestre
        self.creditos = creditos


class RamoEnCurso:

    def __init__(self, sigla, nombre, semestre, creditos):
        self.sigla = sigla
        self.nombre = nombre
        self.semestre = semestre
        self.creditos = creditos