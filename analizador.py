import re as re

def analizador_lexico(programa):

    palabrasReservadas = {
        'inicio', 
        'fin', 
        'entero', 
        'real', 
        'booleano', 
        'Caracter', 
        'cadena', 
        'verdadero',
        'falso',
        'escriba',
        'lea',
        'llamar',
        'si',
        'sino',
        'y',
        'o', 
        'mod',
        'caso',
        


        }
    tokens = [
        ('ENTERO', r'\d+'),
        ('SUMA', r'\+'),
        ('RESTA', r'-'),
        ('MULTIPLICACION', r'\*'),
        ('DIVISION', r'/'),
        ('ESPACIO', r'\s+'),
    ]
    resultado = []
    posicion = 0

    while posicion < len(programa):
        coincidio = False
        for nombre_token, patron in tokens:
            regex = re.compile(patron)
            match = regex.match(programa, posicion)
            if match:
                valor = match.group(0)
                if nombre_token != 'ESPACIO':
                    resultado.append((nombre_token, valor))
                posicion = match.end()
                coincidio = True
                break
        if not coincidio:
            raise Exception('Error: Token no válido en la posición {}'.format(posicion))
    
    return resultado

if __name__ == "__main__":
    # Ejemplo de uso del analizador léxico
    codigo = '3 + 5 * 2 - 1'
    tokens = analizador_lexico(codigo)
    print(tokens)
  

