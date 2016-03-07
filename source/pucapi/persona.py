class Persona:

    def __init__(self, nombre="", mail="", anexo="", categoria="", detalle=""):
        self.nombre = nombre
        self.mail = mail
        self.anexo = anexo
        self.categoria = categoria
        self.detalle = detalle

    def __repr__(self):
        return "{}({}, {})".format(self.nombre, self.mail, self.categoria)