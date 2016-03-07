from PIL import Image
import json
import os.path as path
import io


PATH = path.dirname(path.abspath(__file__))


def __cut_matrix(matrix, end, start=0):
    aux = []
    for i in range(len(matrix)):
        fila = []
        for j in range(start, end):
            fila.append(matrix[i][j])
        aux.append(fila)
    return aux


def __look_for_match(letter, letters_saved):
    for key, value_list in letters_saved.items():
        for value in value_list:
            if len(value) == len(letter):
                if value == letter:
                    return key
    return None


def __print_rgb_matrix(matrix):
    for row in matrix:
        for element in row:
            print("{: ^15}".format(str(element)), end="")
        print()


def __print_letter_template(template):
    for row in template:
        for element in row:
            print("{: ^5}".format(str(element)), end="")
        print()


def __blank_letter(matrix):
    letter = []
    for i in range(len(matrix)):
        letter.append([])
    return letter


def __add_column(matrix_to, matrix_from, row):
    for j in range(len(matrix_from)):
        if __pixel_is_dark(matrix_from[j][row]):
            matrix_to[j].append(matrix_from[j][row])
        else:
            matrix_to[j].append(" ")


def __add_column_template(template, matrix, row):
    for j in range(len(matrix)):
        if __pixel_is_dark(matrix[j][row]):
            template[j].append("X")
        else:
            template[j].append(" ")


def __fila_en_blanco(fila):
    for pixel in fila:
        if __pixel_is_dark(pixel):
            return False
    return True


def __pixel_is_dark(pixel):
    return pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50


def __get_rgb_matrix(img):
    ancho, alto = img.size
    matrix = []
    for h in range(alto):
        row = []
        for a in range(ancho):
            row.append(img.getpixel((a, h)))
        matrix.append(row)
    return matrix


def __get_mail_from_matrix(matrix):
    mail = ""
    with open(PATH + "\letters2.json", "r") as file:
        letters_saved = json.load(file)
    state = "BUSCANDO"
    letter = __blank_letter(matrix)
    for i in range(len(matrix[0])):
        fila = []
        for j in range(len(matrix)):
            fila.append(matrix[j][i])
        if __fila_en_blanco(fila):
            if state == "LEYENDO":
                state = "BUSCANDO"
                mail += __match_letter(letter, letters_saved)
                letter = __blank_letter(matrix)
        else:
            if state == "BUSCANDO":
                state = "LEYENDO"
                __add_column_template(letter, matrix, i)
            elif state == "LEYENDO":
                __add_column_template(letter, matrix, i)
        # with open(PATH + "\letters.json", "w") as file:
        #    json.dump(letters_saved, file, indent=2, sort_keys=True)
    return mail


def get_mail_from_image(bytes):
    stream = io.BytesIO(bytes)
    image = Image.open(stream)
    matrix = __get_rgb_matrix(image)
    return __get_mail_from_matrix(matrix)


def __letter_menu(letter, letters_saved):
    new_letter = letter
    b = ""
    while True:
        __print_letter_template(new_letter)
        print("len:", len(new_letter[0]))
        print("1 Save")
        print("2 Cut")
        print("3 Whole letter")
        print("4 Exit")
        a = input("?: ").strip()
        if a == "1":
            b = input("Letter?: ").strip()
            if b != "":
                key = str(len(new_letter[0]))
                if key in letters_saved:
                    if b in letters_saved[key]:
                        letters_saved[key][b].append(new_letter)
                        break
                    else:
                        letters_saved[key][b] = [new_letter]
                        break
                else:
                    letters_saved[key] = {b: [new_letter]}
                with open(PATH + "/letters2.json", "w") as file:
                    json.dump(letters_saved, file)
        elif a == "2":
            start = int(input("start: "))
            end = int(input("end: "))
            new_letter = __cut_matrix(new_letter, end=end, start=start)
        elif a == "3":
            new_letter = letter
        elif a == "4":
            break
    return b


def __match_letter(letter, letters_saved):

    match = __match_letter_simple(letter, letters_saved)
    if match is not None:
        return match
    else:
        for key in sorted(list(letters_saved.keys()), reverse=True):
            if int(key) <= len(letter[0]):
                sub_letter = __cut_matrix(letter, int(key))
                match = __match_letter_simple(sub_letter, letters_saved)
                if match is not None:
                    return match + __match_letter(__cut_matrix(letter, start=int(key), end=len(letter[0])),
                                                  letters_saved)
        return __letter_menu(letter, letters_saved)


def __match_letter_simple(letter, letters_saved):
    key = str(len(letter[0]))
    if key in letters_saved:
        for l, value_list in letters_saved[key].items():
            for value in value_list:
                if value == letter:
                    return l

# with open(PATH + "letters2.json", "r") as file:
#     saved_letters = json.load(file)
# for key in saved_letters:
#     for key2 in saved_letters[key]:
#         saved_letters[key][key2] = [saved_letters[key][key2]]
# with open("letters2.json", "w") as file:
#     json.dump(saved_letters, file, indent=2, sort_keys=True)