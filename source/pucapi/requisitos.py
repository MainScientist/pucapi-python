class Requisito:

    correquisitos = []

    def __init__(self, string, relacion=None):
        sin_parentesis = Requisito.quitar_parentesis(string)
        if relacion is None:
            self.__relacion = Requisito.__encontrar_relacion(sin_parentesis)
        else:
            self.__relacion = relacion
        self.__curso = None
        self.__requisitos = None
        self.__corequisito = False
        if self.__relacion != "":
            self.__requisitos = []
            subrequisitos = sin_parentesis.split(self.__relacion)
            for subrequisito in subrequisitos:
                s = Requisito.quitar_parentesis(subrequisito)
                self.__requisitos.append(Requisito(s))
        else:
            self.__corequisito = "(c)" in string
            self.__curso = Requisito.quitar_c(string)
            Requisito.correquisitos.append(Requisito.quitar_c(string))

    def cumple_requisito(self, cursos_cursados):
        if self.__curso is not None:
            for curso in cursos_cursados:
                if curso.sigla == self.__curso:
                    return True
            return False
        else:
            if self.__relacion == " o ":
                for requisito in self.__requisitos:
                    if requisito.cumple_requisito(cursos_cursados):
                        return True
                return False
            else:
                for requisito in self.__requisitos:
                    if not requisito.cumple_requisito(cursos_cursados):
                        return False
                return True

    @staticmethod
    def quitar_c(string):
        if "(c)" in string:
            return string[:string.index("(c)")]
        else:
            return string

    @staticmethod
    def __encontrar_relacion(string):
        state = "INIT"
        depth = 0
        for char in string:
            if state == "INIT":
                if char == "(":
                    state = "IGNORING"
                    depth += 1
                else:
                    state = "WAITING_FOR_THE_END"
            elif state == "IGNORING":
                if char == ")" and depth == 1:
                    state = "WAITING_FOR_THE_END"
                elif char == ")":
                    depth -= 1
                elif char == "(":
                    depth += 1
            elif state == "WAITING_FOR_THE_END":
                if char == " ":
                    state = "ENDED"
            elif state == "ENDED":
                if char == "y" or char == "o":
                    return " " + char + " "
        return ""

    @staticmethod
    def quitar_parentesis(string):
        if string[0] == "(":
            return string[1:len(string)-1]
        else:
            return string

    def __repr__(self):
        r = ""
        if self.__curso is None:
            r += "("
            for requisito in self.__requisitos:
                r += str(requisito) + self.__relacion
            if len(self.__requisitos) > 1:
                r = r[:len(r)-3]
            r += ")"
        else:
            r += self.__curso
            if self.__corequisito:
                r += "(c)"
        return r
