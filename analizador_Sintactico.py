import sys
from typing import NamedTuple
import re

class Token(NamedTuple):
    token_type: str
    token_value: str
    line: int
    column: int

def analizador_lexico(frase):

    palabras_reservadas = {'inicio', 'fin', 'entero', 'real', 'booleano', 'caracter', 'cadena', 'verdadero', 'falso', 'escriba', 'lea', 'llamar',
        'si', 'sino', 'y', 'o', 'mod', 'caso', 'mientras', 'haga', 'repita', 'hasta', 'para', 'procedimiento', 'var', 'retorne', 'funcion', 'nueva_linea',
        'registro', 'arreglo', 'de', 'entonces', 'div', 'fin si', 'fin caso', 'fin mientras','fin para', 'fin registro',
        }
    tokens = [
        ('one_line_comment', r'\/\/.*'),
        ('multi_line_comment', r'\/\*([^*]|(\*+[^*/]))*\*+\/'),
        ('tkn_real', r'\d+\.\d+|\d+'),
        ('tkn_assign', r'<-'),
        ('close_fin', r'[Ff]in [Ss]i'),
        ('close_caso', r'[Ff]in  [Cc]aso'),
        ('close_mientras', r'[Ff]in  [Mm]ientras'),
        ('close_para', r'[Ff]in [Pp]ara'),
        ('close_registro', r'[Ff]in [Rr]egistro'),
        ('id', r'[A-Za-z_0-9]+'),
        ('tkn_str', r'"[^"]*"'),
        ('tkn_period', r'\.'),
        ('tkn_comma', r'\,'),
        ('tkn_colon', r'\:'),
        ('tkn_closing_bra', r'\]'),
        ('tkn_opening_bra', r'\['),
        ('tkn_closing_par', r'\)'),
        ('tkn_opening_par', r'\('),
        ('tkn_plus', r'\+'),
        ('tkn_minus', r'\-'),
        ('tkn_times', r'\*'),
        ('tkn_div', r'\/'),
        ('tkn_power', r'\^'),
        ('tkn_neq', r'<>'),
        ('tkn_leq', r'<='),
        ('tkn_less', r'\<'),
        ('tkn_geq', r'>='),
        ('tkn_greater', r'\>'),
        ('tkn_equal', r'\='),
        ('tkn_char', r"'(.)'"),
        ('skip', r'[ \t]+'),
        ('newline', r'\n'),
        ('NiF', r'.'),

    ]

    generadorPatrones = '|'.join('(?P<%s>%s)' % (pair[0], pair[1]) for pair in tokens)
    line_num = 1
    line_start = 0
    iterator = re.finditer(generadorPatrones, frase)
    a = True
    resultado = []

    for mo in iterator:
        token_type = mo.lastgroup
        token_value = mo.group()
        column = (mo.start()+1) - line_start
        if(token_type == 'id' or token_type == 'close_fin' or token_type == 'close_caso' or token_type == 'close_mientras' or token_type == 'close_para' or token_type == 'close_registro'):
            token_value = token_value.lower()
            if(token_value in palabras_reservadas):
              resultado.append(f"<{token_value},{line_num},{column}>")
              if(token_value=='fin' and column == 1):
                 next_line_num = line_num
                 next_line_start = 0
                 while(a == True):
                  try:
                    next_token = next(iterator)
                    next_token_type = next_token.lastgroup
                    next_token_value = next_token.group()
                    next_column = (next_token.start() + 1) - next_line_start
                    if next_token_type == 'newline':
                      next_line_start = next_token.end()
                      next_line_num += 1
                      continue
                    elif next_token_type == 'skip':
                      continue
                    elif(next_token_type == 'one_line_comment' or next_token_type == 'multi_line_comment'):
                      if(next_token_type == 'multi_line_comment'):
                        next_line_num = next_line_num + next_token_value.count('\n')
                      continue
                    if not (next_token_type == 'newline' or next_token_type == 'skip' or token_type == 'one_line_comment' or token_type == 'multi_line_comment'):
                      resultado.append(f'>>> Error lexico (linea: {next_line_num}, posicion: {next_column})')
                      return None
                  except StopIteration:
                    a = False
                    pass
              continue
            resultado.append(f"<{token_type},{token_value},{line_num},{column}>")
            continue

        elif token_type == 'newline':
            line_start = mo.end()
            line_num += 1
            continue
        elif token_type == 'skip':
            continue
        elif token_type == 'NiF':
            resultado.append(f'>>> Error lexico (linea: {line_num}, posicion: {column})')
            return None
        else:
            if(token_type == 'tkn_char'):
                resultado.append(f"<{token_type},{token_value[1]},{line_num},{column}>")
                continue
            if(token_type == 'tkn_str'):
                n=len(token_value)
                if('\n' in token_value):
                  resultado.append(f'>>> Error lexico (linea: {line_num}, posicion: {column})')
                  return None
                resultado.append(repr(f"<{token_type},{token_value[1:(n-1)]},{line_num},{column}>")[1:-1])
                continue
            if(token_type == 'tkn_real'):
                if('.' in token_value):
                    resultado.append(f"<{token_type},{token_value},{line_num},{column}>")
                    continue
                else:
                    token_type = 'tkn_integer'
                    resultado.append(f"<{token_type},{token_value},{line_num},{column}>")
                    continue
            if(token_type == 'one_line_comment' or token_type == 'multi_line_comment'):
                continue
            resultado.append(f"<{token_type},{line_num},{column}>")
            continue
    return resultado
        
    





def analizador_sintactico(tokens):


    # Definición de la posición actual en la lista de tokens
    pos = 0

    # Función para avanzar al siguiente token
    def avanzar():
        global pos
        pos += 1

    # Función para verificar si se ha llegado al final de la entrada
    def fin_de_entrada():
        return pos >= len(tokens)

    # Función para analizar una declaración de variable
    def analizar_declaracion_variable():
        if tokens[pos] == 'VAR':
            avanzar()
            if tokens[pos].startswith('ID'):
                avanzar()
                if tokens[pos] in {'entero', 'real', 'booleano', 'caracter', 'cadena'}:
                    avanzar()
                    if tokens[pos] == ';':
                        avanzar()
                    else:
                        raise SyntaxError("Error de sintaxis: Se esperaba ';' después de la declaración de variable.")
                else:
                    raise SyntaxError("Error de sintaxis: Tipo de dato no válido.")
            else:
                raise SyntaxError("Error de sintaxis: Identificador no válido.")
        else:
            raise SyntaxError("Error de sintaxis: Se esperaba 'VAR'.")

    # Función para analizar una expresión
    def analizar_expresion():
        # Implementa la lógica para analizar expresiones aquí
        pass

    # Función para analizar una declaración de control
    def analizar_declaracion_control():
        if tokens[pos] in {'si', 'mientras', 'para', 'repita'}:
            if tokens[pos] == 'si':
                # Analiza una sentencia "si" aquí
                pass
            elif tokens[pos] == 'mientras':
                # Analiza una sentencia "mientras" aquí
                pass
            elif tokens[pos] == 'para':
                # Analiza una sentencia "para" aquí
                pass
            elif tokens[pos] == 'repita':
                # Analiza una sentencia "repita" aquí
                pass
        else:
            raise SyntaxError("Error de sintaxis: Declaración de control no válida.")

    # Función para analizar una declaración de función
    def analizar_declaracion_funcion():
        if tokens[pos] == 'FUNCION':
            avanzar()
            if tokens[pos].startswith('ID'):
                avanzar()
                if tokens[pos] == '(':
                    avanzar()
                    # Analiza los parámetros de la función
                    while tokens[pos] != ')':
                        if tokens[pos].startswith('ID'):
                            avanzar()
                            if tokens[pos] in {'entero', 'real', 'booleano', 'caracter', 'cadena'}:
                                avanzar()
                                if tokens[pos] == ',':
                                    avanzar()
                                elif tokens[pos] == ')':
                                    avanzar()
                                else:
                                    raise SyntaxError("Error de sintaxis: Se esperaba ',' o ')' en la lista de parámetros.")
                            else:
                                raise SyntaxError("Error de sintaxis: Tipo de dato no válido en la lista de parámetros.")
                        else:
                            raise SyntaxError("Error de sintaxis: Identificador no válido en la lista de parámetros.")
                    # Analiza el tipo de dato de retorno y el cuerpo de la función
                    if tokens[pos] in {'entero', 'real', 'booleano', 'caracter', 'cadena'}:
                        avanzar()
                        # Implementa el análisis del cuerpo de la función aquí
                        pass
                    else:
                        raise SyntaxError("Error de sintaxis: Tipo de dato de retorno no válido.")
                else:
                    raise SyntaxError("Error de sintaxis: Se esperaba '(' después del nombre de la función.")
            else:
                raise SyntaxError("Error de sintaxis: Identificador no válido para la función.")
        else:
            raise SyntaxError("Error de sintaxis: Se esperaba 'FUNCION'.")

    # Función principal para analizar el programa
    def analizar_programa():
        while not fin_de_entrada():
            if tokens[pos] == 'VAR':
                analizar_declaracion_variable()
            elif tokens[pos] in {'si', 'mientras', 'para', 'repita'}:
                analizar_declaracion_control()
            elif tokens[pos] == 'FUNCION':
                analizar_declaracion_funcion()
            else:
                raise SyntaxError("Error de sintaxis: Declaración no válida.")

    # Llamada a la función principal para iniciar el análisis
    analizar_programa()




if __name__ == "__main__":

    #s = sys.stdin.read()

    s= '''funcion my_function : 5
    inicio
        escriba "I wanna return 5"
    fin
    '''
    i = 0
    fraselexica = []

    for i in analizador_lexico(s):
       fraselexica.append(i)

    print(fraselexica)
    analizador_sintactico(fraselexica)
