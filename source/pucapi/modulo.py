class Modulo:
    def __init__(self, dia, numero, sala, tipo, ramo):
        self.dia = dia
        self.numero = numero
        self.sala = sala
        self.tipo = tipo
        self.ramo = ramo

    def topa(self, otro):
        if otro.dia == self.dia and otro.numero == self.numero:
            if otro.tipo == "LAB" or otro.tipo == "CAT":
                if self.tipo == "CAT" or self.tipo == "LAB":
                    return True
        return False
