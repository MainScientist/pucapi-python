from bs4 import BeautifulSoup

"""
Modulo con funciones utiles
"""


def get_jsessionid(portal_html):
    """
    Recibe un html y retorna la jsession que contiene (no se usa).
    """
    method_index = portal_html.find("getSessionId:function()")
    return_index = portal_html.find("return", method_index)
    i = portal_html.find('"', return_index)
    jsessionid = portal_html[i+1:portal_html.find('"', i+1)]
    return jsessionid


def find_data(page):
    form = BeautifulSoup(page, "html.parser").find("form")

    action = form.attrs["action"]
    lt = form.find("input", {"name": "lt"}).attrs["value"]
    execution = form.find("input", {"name": "execution"}).attrs["value"]
    event_id = form.find("input", {"name": "_eventId"}).attrs["value"]

    return {"action": action, "lt": lt, "execution": execution, "_eventId": event_id}