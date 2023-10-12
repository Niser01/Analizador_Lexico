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
        
    
class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0


    def reservadas(self):
        palabras_validas = [
            'inicio', 'fin', 'entero', 'real', 'booleano', 'caracter', 'cadena', 'verdadero', 'falso', 'escriba', 'lea', 'llamar',
            'si', 'sino', 'y', 'o', 'mod', 'caso', 'mientras', 'haga', 'repita', 'hasta', 'para', 'procedimiento', 'var', 'retorne', 'funcion', 'nueva_linea',
            'registro', 'arreglo', 'de', 'entonces', 'div', 'fin si', 'fin caso', 'fin mientras','fin para', 'fin registro'
        ]
        if self.tokens[self.pos][0] in palabras_validas:
            return True
        return False

    def error(self, expected):
        if self.reservadas() or self.tokens[self.pos][0] in ['tkn_comma', 'tkn_assign', 'tkn_opening_par', 'tkn_opening_bra', 'tkn_closing_bra', 'tkn_closing_par', 'tkn_period', 'tkn_colon', 'tkn_plus',
                'tkn_minus', 'tkn_times', 'tkn_div', 'tkn_power', 'tkn_neq', 'tkn_leq', 'tkn_less', 'tkn_geq', 'tkn_greater', 'tkn_equal', 'newline']:
            token_actual = self.tokens[self.pos]
            lexema = token_actual[0]
            fila, columna = token_actual[1], token_actual[2]
            mensaje = f"{fila}:{columna} Error sintáctico: se encontró: {lexema}; se esperaba: {', '.join(expected)}."
        else:
            token_actual = self.tokens[self.pos]
            lexema = token_actual[0]
            fila, columna = token_actual[2], token_actual[3]
            mensaje = f"{fila}:{columna} Error sintáctico: se encontró: {lexema}; se esperaba: {', '.join(expected)}."
        print(mensaje)
        exit()



    def programa(self):
        if self.sentencia():
            if self.programa_Funcion():
                if self.tokens[self.pos][0] == 'EOF':
                    return True
        return False

    def programa_Funcion(self):
        if self.tokens[self.pos][0] == 'newline':
            self.pos += 1  # Avanzar al siguiente token (EoL)
            if self.programa():
                return True
        return True  # Puede ser ε (vacío)


    def sentencia(self):
        if self.declaracion():
            return True
        if self.bloque_programa():
            return True
        if self.asignacion():
            return True
        if self.lectura():
            return True
        if self.escritura():
            return True
        if self.condicional():
            return True
        if self.casos():
            return True
        if self.mientras():
            return True
        if self.repita():
            return True
        if self.para():
            return True
        if self.funcion():
            return True
        if self.procedimiento():
            return True
        if self.registro():
            return True
        if self.arreglo():
            return True
        return False

    def declaracion(self):
        if self.palabras_reservadas():
            if self.identificador():
                if self.declaracion_Ciclo():
                    if self.tokens[self.pos][0] == 'newline':
                        return True
        return False

    def declaracion_Ciclo(self):
        if self.tokens[self.pos][0] == "tkn_comma":
            self.pos += 1 
            if self.declaracion_Ciclo2():
                if self.tokens[self.pos][0] == 'newline':
                    return True
        return True

    def declaracion_Ciclo2(self):
        if self.palabras_reservadas():
            return True
        if self.identificador():
            return True
        if self.palabras_reservadas():
            if self.identificador():
                return True
        return False

    def asignacion(self):
        if self.identificador():
            if self.tokens[self.pos][0] == 'tkn_assign':
                if self.expresion():
                    if self.tokens[self.pos][0] == 'newline':
                        return True
        return False

    def lectura(self):
        if self.tokens[self.pos][0] == 'lea':
            self.pos += 1  
            return self.lectura_Ciclo()
        return False


    def lectura_Ciclo(self):
        if self.identificador():
            if self.token():
                if self.tokens[self.pos][0] == 'newline':
                    if self.lectura_Ciclo():
                        return True
        return True

    def escritura(self):
        if self.tokens[self.pos][0] == 'escriba':
            self.pos +=1
            return self.escritura_Ciclo()
        return False

    def escritura_Ciclo(self):
        if self.identificador():
            if self.token():
                if self.palabras_reservadas():
                    if self.tokens[self.pos][0] == 'newline':
                        if self.escritura_Ciclo():
                            return True
        return True

    def tipo(self):
        tipos_validos = ["entero", "real", "booleano", "caracter", "cadena"]
        if self.tokens[self.pos][0] in tipos_validos:
            self.pos += 1
            return True
        return False

    def identificador(self):
        if self.tokens[self.pos][0] == "id":
            self.pos += 1
            return True
        return False

    def expresion(self):
        return self.expresion_Ciclo()

    def expresion_Ciclo(self):
        if self.factor():
            if self.expresion_Ciclo():
                return True
        return True

    def factor(self):
        if self.token():
            return True
        if self.identificador():
            return True
        if self.palabras_reservadas():
            return True
        if self.expresion():
            return True
        return False

    def palabras_reservadas(self):
        if self.tokens[self.pos][0] == 'inicio':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'fin':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'entero':
            self.pos += 1
            return True    
        if self.tokens[self.pos][0] == 'real':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'booleano':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'caracter':
            self.pos += 1
            return True   
        if self.tokens[self.pos][0] == 'cadena':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'verdadero':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'falso':
            self.pos += 1
            return True    
        if self.tokens[self.pos][0] == 'escriba':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'lea':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'llamar':
            self.pos += 1
            return True   
        if self.tokens[self.pos][0] == 'si':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'sino':
            self.pos += 1
            return True    
        if self.tokens[self.pos][0] == 'y':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'u':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'mod':
            self.pos += 1
            return True    
        if self.tokens[self.pos][0] == 'caso':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'mientras':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'haga':
            self.pos += 1
            return True   
        if self.tokens[self.pos][0] == 'repita':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'hasta':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'para':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'procedimiento':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'var':
            self.pos += 1
            return True   
        if self.tokens[self.pos][0] == 'retorne':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'funcion':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'nueva_linea':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'registro':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'arreglo':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'de':
            self.pos += 1
            return True   
        if self.tokens[self.pos][0] == 'entonces':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'div':
            self.pos += 1
            return True   
        if self.tokens[self.pos][0] == 'fin si':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'fin caso':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'fin mientras':
            self.pos += 1
            return True   
        if self.tokens[self.pos][0] == 'fin para':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'fin registro':
            self.pos += 1
            return True                                                                                                        

    def EoL(self):
        if self.tokens[self.pos][0] == "newline":
            self.pos += 1
            return True
        return False

    def token(self):
        tokens_validos = [
            "tkn_comma", "tkn_assign", "tkn_real", "tkn_integer", "tkn_str",
            "tkn_opening_par", "tkn_opening_bra", "tkn_closing_bra",
            "tkn_closing_par", "tkn_period", "tkn_colon", "tkn_plus",
            "tkn_minus", "tkn_times", "tkn_div", "tkn_power", "tkn_neq",
            "tkn_leq", "tkn_less", "tkn_geq", "tkn_greater", "tkn_equal",
            "tkn_char"
        ]
        if self.tokens[self.pos][0] in tokens_validos:
            self.pos += 1
            return True
        return False


    def condicional(self):
        if self.tokens[self.pos][0] == "si":
            if self.expresion():
                if self.tokens[self.pos][0] == "entonces":
                    if self.sentencia_condicional():
                        return True
        return False

    def sentencia_condicional(self):
        if self.sentencia_acciones():
            return self.sentencia_condicional_Ciclo()
        return False

    def sentencia_condicional_Ciclo(self):
        if self.tokens[self.pos][0] == "sino":
            if self.bloque_sino():
                if self.tokens[self.pos][0] == "fin si":
                    return self.sentencia_condicional_Ciclo()
        return True

    def bloque_sino(self):
        if self.sentencia_acciones():
            return self.bloque_sino_Ciclo()
        return True

    def bloque_sino_Ciclo(self):
        if self.tokens[self.pos][0] == "sino":
            if self.bloque_sino():
                return self.bloque_sino_Ciclo()
        return True

    def casos(self):
        if self.tokens[self.pos][0] == "caso":
            if self.identificador():
                if self.id_casos():
                    if self.tokens[self.pos][0] == "tkn_colon":
                        if self.casos_Ciclo():
                            if self.tokens[self.pos][0] == "sino":
                                if self.casos_Ciclo():
                                    if self.tokens[self.pos][0] == "fin caso":
                                        return True
        return False

    def casos_Ciclo(self):
        if self.sentencia_acciones():
            return True
        return True

    def id_casos(self):
        if self.id_casos_Ciclo():
            if self.tokens[self.pos][0] == "tkn_comma":
                return True
        return True

    def id_casos_Ciclo(self):
        if self.tokens[self.pos][0] in ["tkn_integer", "tkn_real"]:
            self.pos += 1
            return True
        return False

    def mientras(self):
        if self.tokens[self.pos][0] == "mientras":
            if self.expresion():
                if self.tokens[self.pos][0] == "haga":
                    if self.ciclo_mientras():
                        if self.tokens[self.pos][0] == "fin mientras":
                            return True
        return False

    def ciclo_mientras(self):
        if self.sentencia_acciones():
            return self.ciclo_mientras_Ciclo()
        return False

    def ciclo_mientras_Ciclo(self):
        if self.sentencia_acciones():
            return self.ciclo_mientras_Ciclo()
        return True

    def repita(self):
        if self.tokens[self.pos][0] == "repita":
            if self.ciclo_repita():
                if self.tokens[self.pos][0] == "hasta":
                    if self.expresion():
                        return True
        return False

    def ciclo_repita(self):
        if self.sentencia_acciones():
            return self.ciclo_repita_Ciclo()
        return False

    def ciclo_repita_Ciclo(self):
        if self.sentencia_acciones():
            return self.ciclo_repita_Ciclo()
        return True

    def para(self):
        if self.tokens[self.pos][0] == "para":
            if self.expresion():
                if self.tokens[self.pos][0] == "hasta":
                    if self.expresion():
                        if self.tokens[self.pos][0] == "haga":
                            if self.ciclo_para():
                                if self.tokens[self.pos][0] == "fin para":
                                    return True
        return False

    def ciclo_para(self):
        if self.sentencia_acciones():
            return self.ciclo_para_Ciclo()
        return False

    def ciclo_para_Ciclo(self):
        if self.sentencia_acciones():
            return self.ciclo_para_Ciclo()
        return True

    def funcion(self):
        if self.tokens[self.pos][0] == "funcion":
            if self.identificador():
                if self.funcion_Ciclo():
                    if self.tokens[self.pos][0] == "inicio":
                        if self.acciones_funcion():
                            if self.tokens[self.pos][0] == "fin":
                                return True
        return False

    def funcion_Ciclo(self):
        if self.tokens[self.pos][0] == "tkn_colon":
            if self.tipo():
                if self.declaracion():
                    return self.funcion_Ciclo()
        return True

    def procedimiento(self):
        if self.tokens[self.pos][0] == "procedimiento":
            if self.identificador():
                if self.procedimiento_Ciclo():
                    if self.tokens[self.pos][0] == "inicio":
                        if self.acciones_procedimiento():
                            if self.tokens[self.pos][0] == "fin":
                                return True
        return False

    def procedimiento_Ciclo(self):
        if self.sentencia_acciones():
            return self.procedimiento_Ciclo()
        return True

    def acciones_procedimiento(self):
        if self.sentencia_acciones():
            return self.acciones_procedimiento()
        return True

    def registro(self):
        if self.tokens[self.pos][0] == "registro":
            if self.identificador():
                if self.registro_Ciclo():
                    if self.tokens[self.pos][0] == "fin":
                        return True
        return False

    def registro_Ciclo(self):
        if self.declaracion():
            return self.registro_Ciclo()
        return True

    def arreglo(self):
        if self.tokens[self.pos][0] == "arreglo":
            if self.arreglo_Def():
                return True
        return False

    def arreglo_Def(self):
        if self.tokens[self.pos][0] == "tkn_opening_bra":
            if self.tokens[self.pos + 1][0] == "tkn_integer":
                if self.tokens[self.pos + 2][0] == "tkn_closing_bra":
                    if self.tipo():
                        if self.identificador():
                            return self.arreglo_Def()
        return True

    def bloque_programa(self):
        if self.tokens[self.pos][0] == "inicio":
            if self.bloque_programa_Ciclo():
                if self.tokens[self.pos][0] == "fin":
                    return True
        return False

    def bloque_programa_Ciclo(self):
        if self.sentencia_acciones():
            return self.bloque_programa_Ciclo()
        return True

    def sentencia_acciones(self):
        if self.asignacion():
            return True
        if self.lectura():
            return True
        if self.escritura():
            return True
        if self.condicional():
            return True
        if self.casos():
            return True
        if self.mientras():
            return True
        if self.repita():
            return True
        if self.para():
            return True
        return False

    def analizar(self):
        if self.programa():
            print("El análisis sintáctico ha finalizado exitosamente.")
        else:
            self.error(["programa"])


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

    #cadena = "<funcion,1,1>"
    #componentes = cadena.strip("<>").split(',')
    #print(componentes)


    #for i in range (len(fraselexica)):
    #    print(fraselexica[i])

    # Uso del analizador sintáctico
    entrada = [
        ("real", 1, 1), ("id", "n1", 1, 6), ("tkn_comma", 1, 8), ("id", "n2", 1, 9), ("newline", 1, 11),("EOF", 1, 12)
    ]

    analizador = AnalizadorSintactico(entrada)
    analizador.analizar()
