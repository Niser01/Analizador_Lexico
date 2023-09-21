import re as re

def analizador_lexico(programa):

    palabrasReservadas = {
        'inicio', 
        'fin', 
        'entero', 
        'real', 
        'booleano', 
        'caracter', 
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
        'mientras',
        'haga',
        'repita',
        'hasta',
        'para',
        'procedimiento',
        'var',
        'retorne',
        'funcion',
        'nueva_linea',
        'registro',
        'arreglo',
        'de',
        'entonces'

        }
    tokens = [
        ('tkn_integer',   r'\d*'),  
        ('tkn_real',   r'\d+(\.\d*)?'),  
        ('tkn_assign',   r'<-'),                      
        ('id',       r'[A-Za-z]+'),    
        ('tkn_str',       r'[A-Za-z]+'),   
        ('tkn_period',       r'.'),      
        ('tkn_comma',       r','), 
        ('tkn_colon',       r':'), 
        ('tkn_closing_bra',       r']'), 
        ('tkn_opening_bra',       r'['), 
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

    codigo = '3 + 5 * 2 - 1'
    tokens = analizador_lexico(codigo)
    print(tokens)
  

