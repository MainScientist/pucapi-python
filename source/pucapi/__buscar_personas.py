import requests
from bs4 import BeautifulSoup

from pucapi.utils import find_data


def prettify(text):
    return BeautifulSoup(text, "html.parser").prettify()


def obtener_portlet_busca_personas():
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
    portlet = session.post("https://portal.uc.cl/c/portal/render_portlet?p_l_id=10229&p_p_id=BuscaPersonas_"
                           "WAR_LPT004_BuscaPersonas_INSTANCE_eZO6&p_p_lifecycle=0&p_p_state=normal&p_p_mode="
                           "view&p_p_col_id=column-2&p_p_col_pos=0&p_p_col_count=5&currentURL=%2Fweb%2Fhome-"
                           "community%2Finicio%3Fgpi%3D10225", data=data)
    print(prettify(portlet.content))


def buscar_persona():
    url = "https://portal.uc.cl/LPT004_BuscaPersonas/BusquedaSimpleController"
    req = session.post(url, data={"searchSimple": "Reutter Juan"})
    print(prettify(req.content))

session = requests.Session()
login()
obtener_portlet_busca_personas()
buscar_persona()
# url = "https://portal.uc.cl/LPT004_BuscaPersonas/BusquedaSimpleController"
# session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
# session.headers["Content-Type"] = "application/x-www-form-urlencoded"
# session.headers["X-Requested-With"] = "XMLHttpRequest"
# print(session.cookies)
# print(session.headers)
# req = session.post(url, data={"searchSimple": "Pezoa Felipe"})
# print(BeautifulSoup(req.content, "html.parser").prettify())

# print(BeautifulSoup(req.content, "html.parser").prettify())
