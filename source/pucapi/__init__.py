from pucapi.alumnouc import AlumnoUC
"""
Modulo que contiene la funcion para hacer login.
"""


def login(username, password):
    """
    Metodo para hacer login.
    :param username:
    :param password:
    :return: 
    """
    return AlumnoUC(username, password)
