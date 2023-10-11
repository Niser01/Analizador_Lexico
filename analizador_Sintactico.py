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
                      resultado.append(f"<{token_type},{line_num},{column}>")
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
            resultado.append(f"<{token_type},{line_num},{column}>")
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
        
    
class Token:
    def __init__(self, token_type, value, position):
        self.token_type = token_type
        self.value = value
        self.position = position

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.index = 0

    def consume_token(self):
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
            self.index += 1
        else:
            self.current_token = None

    def match_token(self, token_type):
        if self.current_token and self.current_token.token_type == token_type:
            self.consume_token()
        else:
            raise SyntaxError(f"Expected {token_type}, but found {self.current_token.token_type} at position {self.current_token.position}")

    def programa(self):
        self.sentencia()
        self.programa_Funcion()

    def programa_Funcion(self):
        if self.current_token and self.current_token.token_type == 'tkn_newline':
            self.match_token('tkn_newline')
            self.programa()
        else:
            return

    def sentencia(self):
        if self.current_token:
            if self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_booleano' or self.current_token.token_type == 'tkn_caracter' or self.current_token.token_type == 'tkn_cadena':
                self.declaracion()
                self.match_token('tkn_newline')
            elif self.current_token.token_type == 'tkn_id':
                self.asignacion()
                self.match_token('tkn_newline')
            elif self.current_token.token_type == 'tkn_lea':
                self.lectura()
            elif self.current_token.token_type == 'tkn_escriba':
                self.escritura()
            elif self.current_token.token_type == 'tkn_si':
                self.condicional()
            elif self.current_token.token_type == 'tkn_caso':
                self.casos()
            elif self.current_token.token_type == 'tkn_mientras':
                self.mientras()
            elif self.current_token.token_type == 'tkn_repita':
                self.repita()
            elif self.current_token.token_type == 'tkn_para':
                self.para()
            elif self.current_token.token_type == 'tkn_funcion':
                self.funcion()
            elif self.current_token.token_type == 'tkn_procedimiento':
                self.procedimiento()
            elif self.current_token.token_type == 'tkn_registro':
                self.registro()
            elif self.current_token.token_type == 'tkn_arreglo':
                self.arreglo()
            else:
                raise SyntaxError(f"Unexpected token: {self.current_token.token_type} at position {self.current_token.position}")

    def declaracion(self):
        self.tipo()
        self.match_token('tkn_id')
        self.declaracion_Ciclo()
        self.match_token('tkn_newline')

    def declaracion_Ciclo(self):
        if self.current_token and self.current_token.token_type == 'tkn_comma':
            self.match_token('tkn_comma')
            self.declaracion_Ciclo2()
        else:
            return

    def declaracion_Ciclo2(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_booleano' or self.current_token.token_type == 'tkn_caracter' or self.current_token.token_type == 'tkn_cadena'):
            self.tipo()
        elif self.current_token and self.current_token.token_type == 'tkn_id':
            self.match_token('tkn_id')
        elif self.current_token and self.current_token.token_type == 'tkn_opening_par':
            self.match_token('tkn_opening_par')
            self.tipo()
            self.match_token('tkn_id')
            self.match_token('tkn_closing_par')
        else:
            raise SyntaxError(f"Unexpected token in declaration: {self.current_token.token_type} at position {self.current_token.position}")

    def asignacion(self):
        self.match_token('tkn_id')
        self.match_token('tkn_assign')
        self.expresion()
        self.match_token('tkn_newline')

    def lectura(self):
        self.match_token('tkn_lea')
        self.lectura_Ciclo()

    def lectura_Ciclo(self):
        self.match_token('tkn_id')
        self.match_token('tkn_comma')
        self.match_token('tkn_newline')
        self.lectura_Ciclo()
        
    def escritura(self):
        self.match_token('tkn_escriba')
        self.escritura_Ciclo()

    def escritura_Ciclo(self):
        self.match_token('tkn_id')
        self.match_token('tkn_comma')
        self.match_token('tkn_integer' or 'tkn_real' or 'tkn_char' or 'tkn_str' or 'verdadero' or 'falso' or 'tkn_integer')
        self.match_token('tkn_newline')
        self.escritura_Ciclo()

    def tipo(self):
        self.match_token('tkn_integer' or 'tkn_real' or 'tkn_booleano' or 'tkn_caracter' or 'tkn_cadena')

    def expresion(self):
        self.expresion_Ciclo()

    def expresion_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_char' or self.current_token.token_type == 'tkn_str' or self.current_token.token_type == 'verdadero' or self.current_token.token_type == 'falso' or self.current_token.token_type == 'tkn_id' or self.current_token.token_type == 'tkn_opening_par'):
            self.factor()
            self.expresion_Ciclo()
        else:
            return

    def factor(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_char' or self.current_token.token_type == 'tkn_str' or self.current_token.token_type == 'verdadero' or self.current_token.token_type == 'falso'):
            self.match_token('tkn_integer' or 'tkn_real' or 'tkn_char' or 'tkn_str' or 'verdadero' or 'falso')
        elif self.current_token and self.current_token.token_type == 'tkn_id':
            self.match_token('tkn_id')
        elif self.current_token and self.current_token.token_type == 'tkn_opening_par':
            self.match_token('tkn_opening_par')
            self.expresion()
            self.match_token('tkn_closing_par')
        else:
            raise SyntaxError(f"Unexpected token in factor: {self.current_token.token_type} at position {self.current_token.position}")

    def condicional(self):
        self.match_token('tkn_si')
        self.expresion()
        self.match_token('tkn_entonces')
        self.sentencia_condicional()

    def sentencia_condicional(self):
        self.sentencia_acciones()
        self.sentencia_condicional_Ciclo()

    def sentencia_condicional_Ciclo(self):
        if self.current_token and self.current_token.token_type == 'tkn_sino':
            self.match_token('tkn_sino')
            self.bloque_sino()
            self.match_token('tkn_fin_si')
            self.sentencia_condicional_Ciclo()
        else:
            return

    def bloque_sino(self):
        self.sentencia_acciones()
        self.bloque_sino_Ciclo()

    def bloque_sino_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_char' or self.current_token.token_type == 'tkn_str' or self.current_token.token_type == 'verdadero' or self.current_token.token_type == 'falso' or self.current_token.token_type == 'tkn_id' or self.current_token.token_type == 'tkn_lea' or self.current_token.token_type == 'tkn_escriba' or self.current_token.token_type == 'tkn_si' or self.current_token.token_type == 'tkn_caso' or self.current_token.token_type == 'tkn_mientras' or self.current_token.token_type == 'tkn_repita' or self.current_token.token_type == 'tkn_para'):
            self.sentencia_acciones()
            self.bloque_sino_Ciclo()
        else:
            return

    def casos(self):
        self.match_token('tkn_caso')
        self.match_token('tkn_id')
        self.id_casos()
        self.match_token('tkn_colon')
        self.casos_Ciclo()
        self.match_token('tkn_sino')
        self.casos_Ciclo()

    def casos_Ciclo(self):
        self.sentencia_acciones()
        self.casos_Ciclo()

    def id_casos(self):
        self.id_casos_Ciclo()
        self.match_token('tkn_comma')

    def id_casos_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real'):
            self.match_token('tkn_integer' or 'tkn_real')
        else:
            raise SyntaxError(f"Unexpected token in id_casos: {self.current_token.token_type} at position {self.current_token.position}")

    def mientras(self):
        self.match_token('tkn_mientras')
        self.expresion()
        self.match_token('tkn_haga')
        self.ciclo_mientras()
        self.match_token('tkn_fin_mientras')

    def ciclo_mientras(self):
        self.sentencia_acciones()
        self.ciclo_mientras_Ciclo()

    def ciclo_mientras_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_char' or self.current_token.token_type == 'tkn_str' or self.current_token.token_type == 'verdadero' or self.current_token.token_type == 'falso' or self.current_token.token_type == 'tkn_id' or self.current_token.token_type == 'tkn_lea' or self.current_token.token_type == 'tkn_escriba' or self.current_token.token_type == 'tkn_si' or self.current_token.token_type == 'tkn_caso' or self.current_token.token_type == 'tkn_mientras' or self.current_token.token_type == 'tkn_repita' or self.current_token.token_type == 'tkn_para'):
            self.sentencia_acciones()
            self.ciclo_mientras_Ciclo()
        else:
            return

    def repita(self):
        self.match_token('tkn_repita')
        self.ciclo_repita()
        self.match_token('tkn_hasta')
        self.expresion()

    def ciclo_repita(self):
        self.sentencia_acciones()
        self.ciclo_repita_Ciclo()

    def ciclo_repita_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_char' or self.current_token.token_type == 'tkn_str' or self.current_token.token_type == 'verdadero' or self.current_token.token_type == 'falso' or self.current_token.token_type == 'tkn_id' or self.current_token.token_type == 'tkn_lea' or self.current_token.token_type == 'tkn_escriba' or self.current_token.token_type == 'tkn_si' or self.current_token.token_type == 'tkn_caso' or self.current_token.token_type == 'tkn_mientras' or self.current_token.token_type == 'tkn_repita' or self.current_token.token_type == 'tkn_para'):
            self.sentencia_acciones()
            self.ciclo_repita_Ciclo()
        else:
            return

    def para(self):
        self.match_token('tkn_para')
        self.expresion()
        self.match_token('tkn_hasta')
        self.expresion()
        self.match_token('tkn_haga')
        self.ciclo_para()
        self.match_token('tkn_fin_para')

    def ciclo_para(self):
        self.sentencia_acciones()
        self.ciclo_para_Ciclo()

    def ciclo_para_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_char' or self.current_token.token_type == 'tkn_str' or self.current_token.token_type == 'verdadero' or self.current_token.token_type == 'falso' or self.current_token.token_type == 'tkn_id' or self.current_token.token_type == 'tkn_lea' or self.current_token.token_type == 'tkn_escriba' or self.current_token.token_type == 'tkn_si' or self.current_token.token_type == 'tkn_caso' or self.current_token.token_type == 'tkn_mientras' or self.current_token.token_type == 'tkn_repita' or self.current_token.token_type == 'tkn_para'):
            self.sentencia_acciones()
            self.ciclo_para_Ciclo()
        else:
            return

    def procedimiento(self):
        self.match_token('tkn_procedimiento')
        self.match_token('tkn_id')
        self.procedimiento_Ciclo()
        self.match_token('tkn_inicio')
        self.acciones_procedimiento()
        self.match_token('tkn_fin')

    def procedimiento_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_booleano' or self.current_token.token_type == 'tkn_caracter' or self.current_token.token_type == 'tkn_cadena'):
            self.sentencia_acciones()
            self.procedimiento_Ciclo()
        else:
            return

    def acciones_procedimiento(self):
        self.sentencia_acciones()
        self.acciones_procedimiento()

    def funcion(self):
        self.match_token('tkn_funcion')
        self.match_token('tkn_id')
        self.funcion_Ciclo()
        self.match_token('tkn_inicio')
        self.acciones_funcion()
        self.match_token('tkn_fin')

    def funcion_Ciclo(self):
        self.match_token('tkn_colon')
        self.tipo()
        self.declaracion()
        self.funcion_Ciclo()

    def registro(self):
        self.match_token('tkn_registro')
        self.match_token('tkn_id')
        self.registro_Ciclo()
        self.match_token('tkn_fin')

    def registro_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_booleano' or self.current_token.token_type == 'tkn_caracter' or self.current_token.token_type == 'tkn_cadena'):
            self.declaracion()
            self.registro_Ciclo()
        else:
            return

    def arreglo(self):
        self.match_token('tkn_arreglo')
        self.arreglo_Def()

    def arreglo_Def(self):
        self.match_token('tkn_opening_bra')
        self.match_token('tkn_integer')
        self.match_token('tkn_closing_bra')
        self.match_token('tkn_de')
        self.tipo()
        self.match_token('tkn_id')
        self.arreglo_Def()

    def bloque_programa(self):
        self.match_token('tkn_inicio')
        self.bloque_programa_Ciclo()
        self.match_token('tkn_fin')

    def bloque_programa_Ciclo(self):
        if self.current_token and (self.current_token.token_type == 'tkn_integer' or self.current_token.token_type == 'tkn_real' or self.current_token.token_type == 'tkn_char' or self.current_token.token_type == 'tkn_str' or self.current_token.token_type == 'verdadero' or self.current_token.token_type == 'falso' or self.current_token.token_type == 'tkn_id' or self.current_token.token_type == 'tkn_lea' or self.current_token.token_type == 'tkn_escriba' or self.current_token.token_type == 'tkn_si' or self.current_token.token_type == 'tkn_caso' or self.current_token.token_type == 'tkn_mientras' or self.current_token.token_type == 'tkn_repita' or self.current_token.token_type == 'tkn_para'):
            self.sentencia_acciones()
            self.bloque_programa_Ciclo()
        else:
            return

    def sentencia_acciones(self):
        if self.current_token and (self.current_token.token_type == 'tkn_id' or self.current_token.token_type == 'tkn_lea' or self.current_token.token_type == 'tkn_escriba' or self.current_token.token_type == 'tkn_si' or self.current_token.token_type == 'tkn_caso' or self.current_token.token_type == 'tkn_mientras' or self.current_token.token_type == 'tkn_repita' or self.current_token.token_type == 'tkn_para'):
            self.sentencia()
        else:
            raise SyntaxError(f"Unexpected token in sentencia_acciones: {self.current_token.token_type} at position {self.current_token.position}")

    def parse(self):
        self.consume_token()
        self.programa()

# Usage
tokens = [
    Token('tkn_integer', 5, (6, 6)),
    Token('tkn_id', 'x', (7, 6)),
    Token('tkn_assign', None, (7, 7)),
    Token('tkn_integer', 10, (7, 8)),
    Token('tkn_newline', None, (7, 10)),
    Token('tkn_si', None, (8, 6)),
    Token('tkn_integer', 5, (8, 9)),
    Token('tkn_entonces', None, (8, 10)),
    Token('tkn_id', 'x', (8, 12)),
    Token('tkn_assign', None, (8, 13)),
    Token('tkn_integer', 1, (8, 14)),
    Token('tkn_newline', None, (8, 16)),
    Token('tkn_fin_si', None, (9, 6)),
]

parser = Parser(tokens)
parser.parse()





if __name__ == "__main__":

    #s = sys.stdin.read()

    s= '''real n1,n2

Inicio

 n1<-(2/3)*5+2^2
 n2<-50+22 div (14-7) mod 2
 // imprimimos los valores
 escriba n1, ' ' , n2
	 
FIn'''
    i = 0
    fraselexica = []

    for i in analizador_lexico(s):
       fraselexica.append(i)

    cadena = "<funcion,1,1>"
    componentes = cadena.strip("<>").split(',')
    print(componentes)


    for i in range (len(fraselexica)):
        print(fraselexica[i])

