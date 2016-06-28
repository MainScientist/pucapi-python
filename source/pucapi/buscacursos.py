from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from pucapi.ramo import Ramo
from pucapi.requisitos import Requisito
from pucapi.const import *

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
    table = page.find_all("table")[BUSCACURSOS_TABLE_NUMBER]
    table_rows = table.find_all("tr", recursive=False)

    headers = get_headers(table_rows)

    results = []
    _unidad_academica = ""
    for i in range(len(table_rows)):
        row = table_rows[i]
        if row.attrs == {}:
            _unidad_academica = row.text.strip()
        if "class" in row.attrs and row["class"][0] in BUSCACURSOS_RESULT_CLASSES:
            data = row.find_all("td", recursive=False)
            _nombre = data[headers[BUSCACURSOS_NOMBRE]].text.strip()
            _nrc = data[headers[BUSCACURSOS_NRC]].text.strip()
            _seccion = data[headers[BUSCACURSOS_SECCION]].text.strip()
            _sigla = data[headers[BUSCACURSOS_SIGLA]].text.strip()
            _aprob_especial = data[headers[BUSCACURSOS_APROB_ESPECIAL]].text.strip()
            _profesores = data[headers[BUSCACURSOS_PROFESOR]].text.strip().split(",")
            _perm_retiro = data[headers[BUSCACURSOS_RETIRO]].text.strip()
            _campus = data[headers[BUSCACURSOS_CAMPUS]].text.strip()
            _categoria = data[headers[BUSCACURSOS_CATEGORIA]].text.strip()
            _en_ingles = data[headers[BUSCACURSOS_INGLES]].text.strip()

            _creditos = int(data[headers[BUSCACURSOS_CREDITOS]].text)

            _requisitos = buscar_requisitos(_sigla)
            _programa = buscar_programa(_sigla)
            _modulos = get_modulos(data[headers[BUSCACURSOS_HORARIO] + 2])

            ramo = Ramo(_nombre, _nrc, _creditos, _seccion, _profesores, _sigla, _requisitos, _programa, 0, 0, _campus,
                        _unidad_academica, _categoria, _modulos, _perm_retiro, _en_ingles, _aprob_especial)

            results.append(ramo)
    return results


def buscar_curso(semestre="2016-1", seccion="1", sigla="", nombre="", profesor="", campus="TODOS", unidad_academica="TODOS",
                 tipo_horario="TODOS", modulos=None):
    ramos = buscar_cursos(semestre, sigla, nombre, profesor, campus, unidad_academica, tipo_horario, modulos)
    if len(ramos) > 0:
        for ramo in ramos:
            if ramo.seccion == str(seccion):
                return ramo
        else:
            return ramos[0]


def get_headers(table_rows):
    if table_rows == 0:
        return []
    table_headers = table_rows[1].find_all("td", recursive=False)
    headers = {}
    for i in range(len(table_headers)):
        data = table_headers[i]
        headers[data.text] = i
    return headers


def get_modulos(data):
    modulos = []
    table_rows = data.find_all("tr")
    for row in table_rows:
        data = row.find_all("td")
        dias, ms = data[0].text.split(":")
        tipo = data[1].text
        sala = data[2].text
        for day in dias.split("-"):
            for modulo in ms.split(","):
                modulos.append(Modulo(day.strip(), int(modulo), sala.strip(), tipo.strip(), None))
    return modulos


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
