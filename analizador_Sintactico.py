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
        self.expected = []


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
            self.pos += 1  
            if self.programa():
                return True
        return True  


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
        if self.EoL():
            return True
        return False

    def declaracion(self):
        if self.palabras_reservadas():
            if self.identificador():
                if self.declaracion_Ciclo():
                    if self.tokens[self.pos][0] == 'newline':
                        self.pos += 1  
                        return True
        return False

    def declaracion_Ciclo(self):
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1 
            if self.declaracion_Ciclo2():
                if self.tokens[self.pos][0] == 'newline':
                    self.pos += 1  
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
                self.pos += 1
                if self.expresion():
                    if self.tokens[self.pos][0] == 'newline':
                        self.pos += 1  
                        return True
        return False

    def lectura(self):
        if self.tokens[self.pos][0] == 'lea':
            self.pos += 1  
            if self.lectura_Ciclo():
                return True
        return False


    def lectura_Ciclo(self):
        if self.identificador():
            if self.token():
                if self.tokens[self.pos][0] == 'newline':
                    self.pos += 1  
                    if self.lectura_Ciclo():
                        return True
        return True

    def escritura(self):
        if self.tokens[self.pos][0] == 'escriba':
            self.pos +=1
            if self.escritura_Ciclo():
                return True
        return False

    def escritura_Ciclo(self):
        if self.identificador():
            if self.token():
                if self.palabras_reservadas():
                    if self.tokens[self.pos][0] == 'newline':
                        self.pos += 1  
                        if self.escritura_Ciclo():
                            return True
        return True

    def identificador(self):
        if self.tokens[self.pos][0] == "id":
            self.pos += 1
            return True
        return False

    def expresion(self):
        if self.factor_expresion():
            if self.expresion_Ciclo():
                return True
        return False

    def expresion_Ciclo(self):
        if self.factor_expresion():
            if self.expresion_Ciclo_Prime():
                return True
        return True

    def expresion_Ciclo_Prime(self):
        if self.factor_expresion():
            if self.expresion_Ciclo_Prime():
                return True
        return True

    def factor_expresion(self):
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
        return False                                                                                                     

    def EoL(self):
        if self.tokens[self.pos][0] == 'newline':
            self.pos += 1
            return True
        return False

    def token(self):
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'tkn_assign':
            self.pos += 1
            return True             

        if self.tokens[self.pos][0] == 'tkn_real':
            self.pos += 1
            return True 
        
        if self.tokens[self.pos][0] == 'tkn_integer':
            self.pos += 1
            return True   

        if self.tokens[self.pos][0] == 'tkn_str':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'tkn_opening_par':
            self.pos += 1
            return True             

        if self.tokens[self.pos][0] == 'tkn_opening_bra':
            self.pos += 1
            return True 
        
        if self.tokens[self.pos][0] == 'tkn_closing_bra':
            self.pos += 1
            return True

        if self.tokens[self.pos][0] == 'tkn_closing_par':
            self.pos += 1
            return True 
        if self.tokens[self.pos][0] == 'tkn_period':
            self.pos += 1
            return True             

        if self.tokens[self.pos][0] == 'tkn_colon':
            self.pos += 1
            return True 
        
        if self.tokens[self.pos][0] == 'tkn_plus':
            self.pos += 1
            return True   

        if self.tokens[self.pos][0] == 'tkn_minus':
            self.pos += 1
            return True 

        if self.tokens[self.pos][0] == 'tkn_times':
            self.pos += 1
            return True             

        if self.tokens[self.pos][0] == 'tkn_div':
            self.pos += 1
            return True 
        
        if self.tokens[self.pos][0] == 'tkn_power':
            self.pos += 1
            return True   

        if self.tokens[self.pos][0] == 'tkn_neq':
            self.pos += 1
            return True 

        if self.tokens[self.pos][0] == 'tkn_leq':
            self.pos += 1
            return True             

        if self.tokens[self.pos][0] == 'tkn_less':
            self.pos += 1
            return True 
        
        if self.tokens[self.pos][0] == 'tkn_geq':
            self.pos += 1
            return True   

        if self.tokens[self.pos][0] == 'tkn_greater':
            self.pos += 1
            return True 

        if self.tokens[self.pos][0] == 'tkn_equal':
            self.pos += 1
            return True             

        if self.tokens[self.pos][0] == 'tkn_char':
            self.pos += 1
            return True 

        return False


    def condicional(self):
        if self.tokens[self.pos][0] == 'si':
            self.pos += 1
            if self.expresion():
                if self.tokens[self.pos][0] == 'entonces':
                    self.pos += 1
                    if self.sentencia_condicional():
                        if self.tokens[self.pos][0] == 'fin si':
                            self.pos += 1
                            return True
        return False

    def sentencia_condicional(self):
        if self.sentencia_acciones():
            if self.sentencia_condicional_Ciclo():
                return True
        if self.sentencia_acciones():
            return True
        return False

    def sentencia_condicional_Ciclo(self):
        if self.tokens[self.pos][0] == 'sino':
            self.pos += 1
            if self.sentencia_acciones():
                    if self.sentencia_condicional_Ciclo():
                        return True
        return True

    def casos(self):
        if self.tokens[self.pos][0] == 'caso':
            self.pos += 1
            if self.valor_caso():
                if self.tokens[self.pos][0] == 'tkn_colon':
                    self.pos += 1
                    if self.bloque_codigo_caso():
                        if self.tokens[self.pos][0] == 'sino':
                                self.pos += 1
                                if self.bloque_codigo_caso():
                                    if self.tokens[self.pos][0] == 'fin caso':
                                        self.pos += 1
                                        return True
        return False

    def valor_caso(self):
        if self.id_casos_Ciclo():
            if self.valor_caso_tail():
                return True
        return True
    
    def valor_caso_tail(self):
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            if self.id_casos_Ciclo():
                if self.valor_caso_tail():
                    return True
        return True

    def id_casos_Ciclo(self) :
        if self.tokens[self.pos][0] == 'tkn_integer':
            self.pos += 1
            return True
        
        if self.tokens[self.pos][0] == 'tkn_real':
            self.pos += 1
            return True
        return False

    def bloque_codigo_caso(self):
        if self.sentencia_acciones():
            return True
        return True   
    
    def mientras(self):
        if self.tokens[self.pos][0] == 'mientras':
            self.pos += 1
            if self.expresion():
                if self.tokens[self.pos][0] == 'haga':
                    self.pos += 1
                    if self.ciclo_mientras():
                        if self.tokens[self.pos][0] == 'fin mientras':
                            self.pos += 1
                            return True
        return False

    def ciclo_mientras(self):
        if self.sentencia_acciones():
            if self.ciclo_mientras():
                return True
        return True

    def repita(self):
        if self.tokens[self.pos][0] == 'repita':
            self.pos += 1
            if self.ciclo_repita():
                if self.tokens[self.pos][0] == 'hasta':
                    self.pos += 1
                    if self.expresion():
                        return True
        return False

    def ciclo_repita(self):
        if self.sentencia_acciones():
            if self.ciclo_repita():
                return True
        return True

    def para(self):
        if self.tokens[self.pos][0] == 'para':
            self.pos += 1
            if self.expresion():
                if self.tokens[self.pos][0] == 'hasta':
                    self.pos += 1
                    if self.expresion():
                        if self.tokens[self.pos][0] == 'haga':
                            self.pos += 1
                            if self.ciclo_para():
                                if self.tokens[self.pos][0] == 'fin para':
                                    self.pos += 1
                                    return True
        return False

    def ciclo_para(self):
        if self.sentencia_acciones():
            if self.ciclo_para():
                return True
        return True

    def procedimiento(self):
        if self.tokens[self.pos][0] == 'procedimiento':
            self.pos += 1
            if self.identificador():
                if self.procedimiento_Ciclo():
                    if self.tokens[self.pos][0] == 'inicio':
                        self.pos += 1
                        if self.acciones_procedimiento():
                            if self.tokens[self.pos][0] == 'fin':
                                self.pos += 1
                                return True
        return False

    def procedimiento_Ciclo(self):
        if self.sentencia_acciones():
            if self.procedimiento_Ciclo():
                return True
        return True

    def acciones_procedimiento(self):
        if self.sentencia_acciones():
            if self.acciones_procedimiento():
                return True
        return True

    def funcion(self):
        if self.tokens[self.pos][0] == 'funcion':
            self.pos += 1
            if self.identificador():
                if self.funcion_Ciclo():
                    if self.tokens[self.pos][0] == 'inicio':
                        self.pos += 1
                        if self.acciones_funcion():
                            if self.tokens[self.pos][0] == 'fin':
                                self.pos += 1
                                return True
        return False

    def funcion_Ciclo(self):
        if self.declaracion_ciclo_funcion():
            if self.tokens[self.pos][0] == 'tkn_colon':
                self.pos += 1
                if self.palabras_reservadas():
                    return True
        return True
    
    def declaracion_ciclo_funcion(self):
        if self.declaracion():
            if self.declaracion_ciclo_funcion():
                return True
        return True

    def acciones_funcion(self):
        if self.sentencia_acciones():
            if self.acciones_funcion():
                return True
        return True

    def registro(self):
        if self.tokens[self.pos][0] == 'registro':
            self.pos += 1
            if self.identificador():
                if self.registro_Ciclo():
                    if self.tokens[self.pos][0] == 'fin':
                        self.pos += 1
                        return True
        return False

    def registro_Ciclo(self):
        if self.declaracion():
            if self.registro_Ciclo():
                return True
        return True

    def arreglo(self):
        if self.tokens[self.pos][0] == 'arreglo':
            self.pos += 1
            if self.arreglo_Def():
                return True
        return False

    def arreglo_Def(self):
        if self.tokens[self.pos][0] == 'tkn_opening_bra':
            if self.tokens[self.pos + 1][0] == 'tkn_integer':
                if self.tokens[self.pos + 2][0] == 'tkn_closing_bra':
                    if self.tokens[self.pos + 2][0] == 'de':
                        if self.palabras_reservadas():
                            if self.identificador():
                                return True
        return True

    def bloque_programa(self):
        if self.tokens[self.pos][0] == 'inicio':
            self.pos += 1  
            if self.bloque_programa_Ciclo():
                if self.tokens[self.pos][0] == 'fin':
                    self.pos += 1  
                    return True
        return False

    def bloque_programa_Ciclo(self):
        if self.sentencia_acciones():
            if self.bloque_programa_Ciclo():
                return True
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
        if self.EoL():
            return True
        return False

    def analizar(self):
        print(self.tokens)
        if self.programa():
            print("El análisis sintáctico ha finalizado exitosamente.")
        else:
            self.error(self.expected)


if __name__ == "__main__":

    #s = sys.stdin.read()

    s= '''inicio
	si 20<2^2 entonces
		escriba "20 es menor que 2 elevado a la 2"
	sino
		escriba "20 no es menor que 2 elevado a la 2"
	fin si
fin
'''
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
        ('inicio',1,1), 
        ('newline',1,7), 
        ('si',2,2), 
        ('tkn_integer',20,2,5), 
        ('tkn_less',2,7),
        ('tkn_integer',2,2,8), 
        ('tkn_power',2,9), 
        ('tkn_integer',2,2,10),
        ('entonces',2,12), 
        ('newline',2,20), 
        ('escriba',3,3),
        ('tkn_str','20 es menor que 2 elevado a la 2',3,11), 
        ('newline',3,45), 
        ('sino',4,2),
        ('newline',4,6), 
        ('escriba',5,3),
        ('tkn_str','20 no es menor que 2 elevado a la 2',5,11), 
        ('newline',5,48), 
        ('fin si',6,2),
        ('newline',6,8),
        ('fin',7,1),  
        ("EOF", 7, 2)
    ]

    analizador = AnalizadorSintactico(entrada)
    analizador.analizar()
