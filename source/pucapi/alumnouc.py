import requests
import time
from bs4 import BeautifulSoup
from pucapi.exceptions import *
from pucapi.ficha_academica import FichaAcademica
from pucapi.__image import get_mail_from_image
from pucapi.persona import Persona
from pucapi.utils import find_data

from pucapi.buscacursos import buscar_curso


class AlumnoUC:
    """
    Clase Alumno UC
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()

        #: Nombre del alumno
        self.nombre = ""
        self.numero_de_alumno = ""

        #: Ruto del alumno
        self.rut = ""

        self.ramos = []
        self.carrera = ""
        self.fecha_nac = ""
        self.genero = ""
        self.pais = ""

        self.generacion = ""

        self.situacion = ""
        self.ficha_academica = FichaAcademica(self)
        self._portal_login()

    def _portal_login(self):
        self.session = requests.Session()
        portal_url = "http://portal.uc.cl"
        req2 = requests.get(portal_url)
        page_data = find_data(req2.content.decode("UTF-8"))
        post_data = {"execution": page_data["execution"],
                     "_eventId": page_data["_eventId"],
                     "lt": page_data["lt"],
                     "username": self.username,
                     "password": self.password}
        portal_response = self.session.post("https://sso.uc.cl" + page_data["action"], data=post_data)
        self.__leer_html_portal(portal_response.content.decode("UTF-8"))

    @property
    def pga(self):
        """
        Calcula y retorna el PGA del alumno.
        """
        ppa = 0
        sum_creditos = sum(float(ramo_cursado.creditos)
                           for semestre in self.ficha_academica.semestres for ramo_cursado in semestre.ramos_cursados)
        print(sum_creditos)
        if sum_creditos > 0:
            for semestre in self.ficha_academica.semestres:
                for ramo_cursado in semestre.ramos_cursados:
                    if float(ramo_cursado.creditos) > 0:
                        ppa += float(ramo_cursado.nota) * float(ramo_cursado.creditos) / sum_creditos
        return ppa

    @property
    def ramos_cursados(self):
        return [ramo for semestre in self.ficha_academica.semestres for ramo in semestre.ramos_cursados]

    def cumple_requisitos(self, ramo):
        return ramo.alumno_cumple_requisitos(self)

    def __leer_html_portal(self, portal_html):
        parsed_portal = BeautifulSoup(portal_html, "html.parser")
        name_li = parsed_portal.find("li", {"class": "greeting"})
        if name_li is None:
            raise LoginError
        self.nombre = name_li.text
        self.__obtener_datos_personales()
        self.__obtener_informacion_academica()

    def __obtener_datos_personales(self):
        url = "https://portal.uc.cl/web/home-community/datos-personales?gpi=10225"
        page_request = self.session.get(url)
        page = BeautifulSoup(page_request.content.decode("UTF-8"), "html.parser")
        scripts = page.find_all("script")
        if len(scripts) < 34:
            raise SessionExpired
        # Personal Data
        data_script = scripts[34]
        i = data_script.text.find('"', data_script.text.find("url:"))+1
        link = data_script.text[i:data_script.text.find('"', i)]

        data = {
            "currentUrl": "/web/home-community/datos-personales?gpi=10225",
            'p_l_id': '10230',
            'p_p_id': 'DatosPersonales_WAR_LPT022_DatosPersonales',
            'p_p_lifecycle': '0',
            'p_p_state': 'normal',
            'p_p_mode': 'view',
            'p_p_col_id': 'column-1',
            'p_p_col_pos': '0',
            'p_p_col_count': '1'
        }
        data_request = self.session.post("https://portal.uc.cl" + link, data=data)
        data_div = BeautifulSoup(data_request.content, "html.parser")
        data_table = data_div.find("table")
        for tr in data_table.find_all("tr"):
            if tr.find("th").text == "RUT":
                self.rut = tr.find("td").text
            elif tr.find("th").text == "Sexo":
                self.genero = tr.find("td").text
            elif tr.find("th").text == "Fecha de Nacimiento":
                self.fecha_nac = tr.find("td").text
            elif tr.find("th").text == "País de Origen":
                self.pais = tr.find("td").text

        # PUC PERSON DATA
        puc_person_script = scripts[35]
        i = puc_person_script.text.find('"', puc_person_script.text.find("url:"))+1
        link = puc_person_script.text[i:puc_person_script.text.find('"', i)]

        data = {
            "currentUrl": "/web/home-community/datos-personales?gpi=10225",
            'p_l_id': '10230',
            'p_p_id': 'infopersona_WAR_LPT008_InfoPersonas_INSTANCE_R5fG',
            'p_p_lifecycle': '0',
            'p_p_state': 'normal',
            'p_p_mode': 'view',
            'p_p_col_id': 'column-1',
            'p_p_col_pos': '0',
            'p_p_col_count': '1'
        }
        data_request = self.session.post("https://portal.uc.cl" + link, data=data)
        puc_person_div = BeautifulSoup(data_request.content.decode("UTF-8"), "html.parser")
        tds = puc_person_div.find_all("td", {"class": "IP-alumno-td"})
        self.numero_de_alumno = tds[0].text
        self.carrera = tds[1].text
        self.generacion = tds[2].text
        self.situacion = tds[4].text

    def __obtener_informacion_academica(self):
        url = "https://portal.uc.cl/web/home-community/informacion-academica?gpi=10225"
        page_request = self.session.get(url)
        page = BeautifulSoup(page_request.content.decode("UTF-8"), "html.parser")
        scripts = page.find_all("script")
        schedule_script = scripts[37]
        i = schedule_script.text.find('"', schedule_script.text.find("url:")) + 1
        schedule_url = schedule_script.text[i: schedule_script.text.find('"', i)]
        data = {
            "currentUrl": "/web/home-community/informacion-academica?gpi=10225",
            'p_l_id': '10706',
            'p_p_id': 'horarioClases_WAR_LPT002_HorarioClases_INSTANCE_uXS5',
            'p_p_lifecycle': '0',
            'p_p_state': 'normal',
            'p_p_mode': 'view',
            'p_p_col_id': 'column-1',
            'p_p_col_pos': '1',
            'p_p_col_count': '8'
        }
        schedule_request = self.session.post("https://portal.uc.cl" + schedule_url, data=data)
        schedule_page = BeautifulSoup(schedule_request.content, "html.parser")
        tds = schedule_page.find_all("td", {"class": "hc-uportal-td2 hc-td"})
        for td in tds:
            sigla, seccion = td.text.split("-")
            ramo = buscar_curso(sigla=sigla, seccion=seccion)
            if ramo is not None:
                self.ramos.append(ramo)

    def buscar_persona_simple(self, nombre):
        self.__obtener_portlet_buscar_personas()
        return self.__buscar_persona_simple(nombre)

    def __obtener_portlet_buscar_personas(self):
        data = {
            "currentUrl": "/web/home-community/inicio?gpi=10225",
            'p_l_id': '10229',
            'p_p_id': 'BuscaPersonas_WAR_LPT004_BuscaPersonas_INSTANCE_eZO6',
            'p_p_lifecycle': '0',
            'p_p_state': 'normal',
            'p_p_mode': 'view',
            'p_p_col_id': 'column-1',
            'p_p_col_pos': '0',
            'p_p_col_count': '5'
        }
        self.session.post("https://portal.uc.cl/c/portal/render_portlet?p_l_id=10229&p_p_id=BuscaPersonas_"
                          "WAR_LPT004_BuscaPersonas_INSTANCE_eZO6&p_p_lifecycle=0&p_p_state=normal&p_p_mode="
                          "view&p_p_col_id=column-2&p_p_col_pos=0&p_p_col_count=5&currentURL=%2Fweb%2Fhome-"
                          "community%2Finicio%3Fgpi%3D10225", data=data)

    def __buscar_persona_simple(self, nombre):
        url = "https://portal.uc.cl/LPT004_BuscaPersonas/BusquedaSimpleController"
        req = self.session.post(url, data={"searchSimple": nombre})
        div = BeautifulSoup(req.content.decode("windows-1252"), "html.parser")
        tbody = div.find("tbody")
        trs = tbody.find_all("tr")
        personas = []
        persona = None
        for tr in trs:
            if "id" in tr.attrs:
                form = tr.find("form", {"name": "BP_frm_email"})
                id = form.attrs["id"][form.attrs["id"].index("email_")+6:]
                req = self.session.get("https://portal.uc.cl/LPT004_BuscaPersonas/TextImage?id="+id,
                                       data={"id": id})
                mail_image = req.content
                mail = get_mail_from_image(mail_image)
                persona.mail = mail
                personas.append(persona)
            else:
                tds = tr.find_all("td")
                if len(tds) > 5:
                    nombre = tds[2].text
                    categoria = tds[5].text.replace("\n", ", ").strip(", ")
                    detalle_td = tds[6]
                    keys = detalle_td.find_all("th")
                    values = detalle_td.find_all("td")
                    detalle = {}
                    for i in range(0, len(keys)):
                        key = keys[i]
                        value = values[i]
                        detalle[key.text] = value.text.replace("\n", "")
                    persona = Persona(nombre=nombre, categoria=categoria, detalle=detalle)
                    # print(tr.prettify())
        return personas
