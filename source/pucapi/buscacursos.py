from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from pucapi.ramo import Ramo
from pucapi.requisitos import Requisito

from pucapi.modulo import Modulo

__cache_programas = {}
__cache_requisitos  = {}


def buscar_cursos(semestre="2016-1", sigla="", nombre="", profesor="", campus="TODOS", unidad_academica="TODOS",
                  tipo_horario="TODOS", modulos=None):
    query = {
        "cxml_semestre": semestre,
        "cxml_sigla": sigla,
        "cxml_nombre": nombre,
        "cxml_profesor": profesor,
        "cxml_campus": campus,
        "cxml_unidad_academica": unidad_academica,
        "cxml_horario_tipo_busqueda": "si_tenga",
        "cxml_horario_tipo_busqueda_actividad": tipo_horario
    }
    if modulos is not None:
        for modulo in modulos:
            query["cxml_modulo_"+modulo] = modulo
    url = "http://buscacursos.uc.cl/?" + urlencode(query)
    response = requests.get(url)
    page = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
    academic_units = page.find_all("td", {"style": "text-align:center; font-weight:bold; font-size:16px; color:#FFFFFF;"
                                                   " background:#1730A6; padding:2px; margin:2px"})
    academic_dic = {}
    for academic_unit in academic_units:
        academic_dic[str(page).index(str(academic_unit))] = academic_unit.text
    trs = page.find_all("tr", {"class": "resultadosRowImpar"}) + page.find_all("tr", {"class": "resultadosRowPar"})
    results = []
    for tr in trs:
        max = 0
        academic_unit = ""
        tr_index = str(page).index(str(tr))
        for key in academic_dic:
            if tr_index > key > max:
                max = key
                academic_unit = academic_dic[key]
        tds = tr.find_all("td")
        r = Ramo(nombre=str(tds[7].text), nrc=str(tds[0].text), creditos=str(tds[10].text), seccion=int(tds[4].text),
                 profesores=str(tds[8].text.split(",")), sigla=str(tds[1].text.replace(" ", "")),
                 programa=buscar_programa(tds[1].text.replace(" ", "")),
                 requisitos=buscar_requisitos(sigla), campus=tds[9].text, unidad_academica=academic_unit)
        if len(tds) > 15:
            tds = tds[14].find_all("td")
            i = 0
            while i <= len(tds) - 3:
                print(tds[i].text)
                days, modulos = tds[i].text.split(":")
                tipo = tds[i+1].text
                sala = tds[i+2].text
                for day in days.split("-"):
                    for modulo in modulos.split(","):
                        r.modulos.append(Modulo(day, modulo, sala, tipo, r))
                i += 3
        results.append(r)
    return sorted(results, key=lambda ramo: (ramo.unidad_academica, ramo.sigla, ramo.seccion))


def buscar_curso(semestre="2016-1", seccion="1", sigla="", nombre="", profesor="", campus="TODOS", unidad_academica="TODOS",
                 tipo_horario="TODOS", modulos=None):
    ramos = buscar_cursos(semestre, sigla, nombre, profesor, campus, unidad_academica, tipo_horario, modulos)
    if len(ramos) > 0:
        for ramo in ramos:
            if ramo.seccion == str(seccion):
                return ramo
        else:
            return ramos[0]


def buscar_programa(sigla):
    if sigla in __cache_programas:
        return __cache_programas[sigla]
    else:
        url = "http://catalogo.uc.cl/index.php?tmpl=component&option=com_catalogo&view=programa&sigla={}".format(sigla)
        response = requests.get(url)
        page = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        div = page.find("div", {"class": "bloque"})
        __cache_programas[sigla] = div.text
        return div.text


def buscar_requisitos(sigla):
    if sigla in __cache_requisitos:
        return __cache_requisitos[sigla]
    else:
        url = "http://catalogo.uc.cl/index.php?tmpl=component&option=com_catalogo&view=requisitos&sigla={}".format(sigla)
        response = requests.get(url)
        page = BeautifulSoup(response.content.decode("windows_1252"), "html.parser")
        requisitos = page.find("tr", {"class": "ui-widget-content even"}).find("span").text
        if "No tiene" in requisitos:
            __cache_requisitos[sigla] = None
            return None
        requisitos = Requisito(requisitos)
        __cache_requisitos[sigla] = requisitos
        return requisitos
