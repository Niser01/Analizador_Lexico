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
        'registro', 'arreglo', 'de', 'entonces', 'div', 'fin si', 'fin caso', 'fin mientras','fin para', 'fin registro'
        }
    tokens = [
        ('one_line_comment', r'\/\/.*'),
        ('multi_line_comment', r'\/\*([^*]|(\*+[^*/]))*\*+\/'),
        ('tkn_real', r'\d+\.\d+|\d+'),
        ('tkn_assign', r'<-'),
        ('close_fin', r'[Ff]in [Ss]i'),
        ('close_caso', r'[Ff]in [Cc]aso'),
        ('close_mientras', r'[Ff]in [Mm]ientras'),
        ('close_para', r'[Ff]in [Pp]ara'),
        ('close_registro', r'[Ff]in [Rr]egistro'),
        ('nueva_linea', r'nueva_linea'),
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
        if(token_type == 'close_fin' or token_type == 'close_caso' or token_type == 'close_mientras' or token_type == 'close_para' or token_type == 'close_registro' or token_type == 'id'):
            token_value = token_value.lower()
            if(token_value in palabras_reservadas):
                resultado.append(f"<{token_value},{line_num},{column}>")
            else:
                resultado.append(f"<{token_type},{token_value},{line_num},{column}>")
            continue

        elif token_type == 'newline' or token_type == 'nueva_linea':
            token_type = 'newline'
            resultado.append(f"<{token_type},{line_num},{column}>")
            line_start = mo.end()
            line_num += 1
            continue
        elif token_type == 'skip':
            continue
        elif token_type == 'NiF':
            resultado.append(f'>>> Error lexico (linea: {line_num}, posicion: {column})')
            return resultado
        else:
            if(token_type == 'tkn_char'):
                resultado.append(f"<{token_type},{token_value[1]},{line_num},{column}>")
                continue
            if(token_type == 'tkn_str'):
                n=len(token_value)
                if('\n' in token_value):
                  resultado.append(f'>>> Error lexico (linea: {line_num}, posicion: {column})')
                  return resultado
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
                if (token_type == 'multi_line_comment'):
                    lineas = 1
                    for caracter in token_value:
                        if caracter == '\n':
                            line_num += 1
                continue

            resultado.append(f"<{token_type},{line_num},{column}>")
            continue
    resultado.append(f"<EOF,{line_num + 1},{1}>")
    return resultado




class AnalizadorSintactico:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.abiertos = 0
        self.cerrados = 0
        self.expected = []
        self.roto = False

    def reservadas(self):
        palabras_validas = [
            'inicio', 'fin', 'entero', 'real', 'booleano', 'caracter', 'cadena', 'verdadero', 'falso', 'escriba', 'lea', 'llamar',
            'si', 'sino', 'y', 'o', 'mod', 'caso', 'mientras', 'haga', 'repita', 'hasta', 'para', 'procedimiento', 'var', 'retorne', 'funcion', 'nueva_linea',
            'registro', 'arreglo', 'de', 'entonces', 'div', 'fin si', 'fin caso', 'fin mientras','fin para', 'fin registro', 'EOF'
        ]
        if self.tokens[self.pos][0] in palabras_validas:
            return True
        return False

    def error(self, metodo, submetodo):

        if metodo == "programa":
            if submetodo == "EOF":
                self.expected.append('"final de archivo"')

        if metodo == "sentencia":
            if submetodo == "conjunto":
                expected = ['"arreglo"', '"booleano"', '"cadena"', '"caracter"', '"entero"', '"funcion"', '"id"', '"inicio"', '"procedimiento"', '"real"', '"registro"']                                             
                for i in expected:
                    self.expected.append(i)
            if submetodo == "sentencia_acciones":
                expected = ['"arreglo"', '"booleano"', '"cadena"', '"caracter"', '"entero"', '"funcion"', '"id"', '"inicio"', '"procedimiento"', '"real"', '","']                                             
                for i in expected:
                    self.expected.append(i)
 
                          
        if metodo == "condicional":
            if submetodo == "expresion":
                expected = ['"cadena_de_caracteres"', '"caracter_simple"', '"falso"', '"id"', '"mod"', '"o"', '"("', '")"', '"*"', '"+"', '"-"', '"."', '"/"', '"<"', '"<="', '"<>"', '"="', '">"', '">="', '"]"', '"valor_entero"', '"valor_real"', '"var"', '"verdadero"', '"y"']                
                for i in expected:
                    self.expected.append(i)
            if submetodo == "entonces":
                self.expected.append('"entonces"')
            if submetodo == "sentencia_condicional":
                self.expected.append()
            if submetodo == "fin_si":   
                self.expected.append('"fin si"')

        if metodo == "llamada":
            if submetodo == "llamar_procedimiento_id":
                self.expected.append('"id"')
            if submetodo == "llamar_procedimiento_expresion":
                expected = ['"cadena_de_caracteres"', '"caracter_simple"', '"falso"', '"id"', '"mod"', '"o"', '"("', '")"', '"*"', '"+"', '"-"', '"."', '"/"', '"<"', '"<="', '"<>"', '"="', '">"', '">="', '"]"', '"valor_entero"', '"valor_real"', '"var"', '"verdadero"', '"y"']                
                for i in expected:
                    self.expected.append(i) 
                      

        if metodo == "declaracion_cadena":            
            if submetodo == "tkn_opening_bra":
                self.expected.append('"["')
            if submetodo == "tkn_integer":
                self.expected.append('"entero"')
            if submetodo == "tkn_closing_bra":
                self.expected.append('"]"')
            if submetodo == "identificador":
                self.expected.append('"id"')

        if metodo == "declaracion_arreglo":            
            if submetodo == "tkn_opening_bra":
                self.expected.append('"["')
            if submetodo == "tkn_closing_bra":
                self.expected.append('"]"')
            if submetodo == "identificador":
                self.expected.append('"id"')                
            if submetodo == "de":
                self.expected.append('"de"')
            if submetodo == "tipo_de_dato":
                expected = ['"booleano"', '"cadena"', '"caracter"', '"entero"', '"real"']
                for i in expected:
                    self.expected.append(i) 
            if submetodo == "tkn_integer":
                self.expected.append('"entero"')         
  
        if metodo == "declaracion":            
            if submetodo == "identificador":
                self.expected.append('"id"')
            if submetodo == "EoL":
                self.expected.append('"nueva_linea"')
            if submetodo == "tipo_de_dato":
                expected = ['"booleano"', '"cadena"', '"caracter"', '"entero"', '"real"']
                for i in expected:
                    self.expected.append(i) 

               
        if metodo == "asignacion":            
            if submetodo == "tkn_assign":
                expected = ['"<-"', '"["', '"."']                
                for i in expected:
                    self.expected.append(i)
            if submetodo == "expresion":
                expected = ['"cadena_de_caracteres"', '"caracter_simple"', '"falso"', '"id"', '"mod"', '"o"', '"("', '")"', '"*"', '"+"', '"-"', '"."', '"/"', '"<"', '"<="', '"<>"', '"="', '">"', '">="', '"]"', '"valor_entero"', '"valor_real"', '"var"', '"verdadero"', '"y"']                
                for i in expected:
                    self.expected.append(i) 
            if submetodo == "EoL":
                self.expected.append('"nueva_linea"')
            if submetodo == "identificador":
                self.expected.append('"id"')    
            if submetodo == "tkn_closing_bra":  
                self.expected.append('"]"')     
            if submetodo == "tipoDato_asignacion":
                expected = ['"entero"', '"id"']                
                for i in expected:
                    self.expected.append(i) 

        if metodo == "lectura":            
            if submetodo == "identificador":
                self.expected.append('"id"')
            if submetodo == "EoL":
                self.expected.append('"nueva_linea"')

        if metodo == "escritura":            
            if submetodo == "palabras_reservadas":
                expected = ['"cadena_de_caracteres"', '"caracter_simple"', '"falso"', '"id"', '"-"', '"("', '"valor_entero"', '"valor_real"', '"verdadero"']
                for i in expected:
                    self.expected.append(i) 
            if submetodo == "EoL":
                self.expected.append('"nueva_linea"')

        if metodo == "expresion":            
            if submetodo == "parentesis":
                while(self.tokens[self.pos][0] == 'newline'):
                    self.pos +=1
                expected = ['"div"', '"mod"', '"o"', '")"', '"/"', '"="', '">="', '">"', '"<="', '"<"', '"-"', '"<>"', '"+"', '"^"', '"*"', '"y"']    
                for i in expected:
                    self.expected.append(i) 

        if metodo == "palabras_reservadas":            
            if submetodo == "palabras_reservadas":
                expected = ['"booleano"', '"cadena"', '"caracter"', '"div"', '"entero"', '"falso"', '"mod"', '"o"', '"real"', '"retorne"', '"var"', '"verdadero"', '"y"']
                for i in expected:
                    self.expected.append(i) 

        if metodo == "casos":            
            if submetodo == "tkn_colon":
                self.expected.append('":"')
            if submetodo == "fin_caso":
                self.expected.append('"fin caso"')    
            if submetodo == "sino":
                self.expected.append('"sino"') 
            if submetodo == "tkn_integer":
                self.expected.append('"entero"') 
            if submetodo == "bloque_codigo_caso":
                expected = ['"caso"', '"escriba"', '"fin"', '"id"', '"lea"', '"llamar"', '"mientras"', '"para"', '"repita"', '"si"']
                for i in expected:
                    self.expected.append(i)
            if submetodo == "tkn_comma_tkn_colon":
                expected = ['":"', '","']
                for i in expected:
                    self.expected.append(i)                    

           
        if metodo == "mientras":            
            if submetodo == "fin mientras": 
                self.expected.append('"fin mientras"')   
            if submetodo == "haga": 
                self.expected.append('"haga"') 
            if submetodo == "expresion":
                expected = ['"cadena_de_caracteres"', '"caracter_simple"', '"falso"', '"id"', '"mod"', '"o"', '"("', '")"', '"*"', '"+"', '"-"', '"."', '"/"', '"<"', '"<="', '"<>"', '"="', '">"', '">="', '"]"', '"valor_entero"', '"valor_real"', '"var"', '"verdadero"', '"y"']                
                for i in expected:
                    self.expected.append(i)    
            if submetodo == "ciclo_mientras":
                expected = ['"caso"', '"escriba"', '"fin"', '"id"', '"lea"', '"llamar"', '"mientras"', '"para"', '"repita"', '"si"']
                for i in expected:
                    self.expected.append(i)        

        if metodo == "repita":            
            if submetodo == "hasta": 
                self.expected.append('"hasta"') 
            if submetodo == "expresion":
                expected = ['"cadena_de_caracteres"', '"caracter_simple"', '"falso"', '"id"', '"mod"', '"o"', '"("', '")"', '"*"', '"+"', '"-"', '"."', '"/"', '"<"', '"<="', '"<>"', '"="', '">"', '">="', '"]"', '"valor_entero"', '"valor_real"', '"var"', '"verdadero"', '"y"']                
                for i in expected:
                    self.expected.append(i) 
            if submetodo == "ciclo_repita":
                expected = ['"caso"', '"escriba"', '"fin"', '"id"', '"lea"', '"llamar"', '"mientras"', '"para"', '"repita"', '"si"']
                for i in expected:
                    self.expected.append(i) 

        if metodo == "para":            
            if submetodo == "fin_para": 
                self.expected.append('"fin para"')
            if submetodo == "haga": 
                self.expected.append('"haga"')
            if submetodo == "expresion":
                expected = ['"cadena_de_caracteres"', '"caracter_simple"', '"falso"', '"id"', '"mod"', '"o"', '"("', '")"', '"*"', '"+"', '"-"', '"."', '"/"', '"<"', '"<="', '"<>"', '"="', '">"', '">="', '"]"', '"valor_entero"', '"valor_real"', '"var"', '"verdadero"', '"y"']                
                for i in expected:
                    self.expected.append(i)
            if submetodo == "hasta": 
                self.expected.append('"hasta"')
            if submetodo == "ciclo_para":
                expected = ['"caso"', '"escriba"', '"fin"', '"id"', '"lea"', '"llamar"', '"mientras"', '"para"', '"repita"', '"si"']
                for i in expected:
                    self.expected.append(i)               

        if metodo == "registro":            
            if submetodo == "fin registro":
                self.expected.append('"fin registro"') 
            if submetodo == "identificador":
                self.expected.append('"id"')   
            if submetodo == "registro_Ciclo":
                expected = ['"arreglo"', '"booleano"', '"cadena"', '"caracter"', '"entero"', '"id"', '"real"', '"var"']
                for i in expected:
                    self.expected.append(i)                             

        if metodo == "bloque_programa":            
            if submetodo == "fin":
                self.expected.append('"fin"') 

        if metodo == "procedimiento":            
            if submetodo == "procedimiento_Ciclo":
                expected = ['"caso"', '"escriba"', '"fin"', '"id"', '"lea"', '"llamar"', '"mientras"', '"para"', '"repita"', '"si"']
                for i in expected:
                    self.expected.append(i) 
            if submetodo == "fin":
                self.expected.append('"fin"')
            if submetodo == "inicio":
                self.expected.append('"inicio"')
            if submetodo == "declaracion":
                expected = ['"arreglo"', '"booleano"', '"cadena"', '"caracter"', '"entero"', '"id"', '"inicio"', '"real"', '"("']
                for i in expected:
                    self.expected.append(i) 
            if submetodo == "identificador":
                self.expected.append('"id"')                                     
            if submetodo == "tkn_closing_par":
                self.expected.append('")"')             
            if submetodo == "parametros_procedimiento":
                expected = ['"arreglo"', '"booleano"', '"cadena"', '"caracter"', '"entero"', '"id"', '"inicio"', '"real"', '"("']
                for i in expected:
                    self.expected.append(i) 

        if metodo == "funcion":            
            if submetodo == "inicio":
                expected = ['"arreglo"', '"booleano"', '"cadena"', '"caracter"', '"entero"', '"id"', '"inicio"', '"real"']
                for i in expected:
                    self.expected.append(i) 
            if submetodo == "fin":
                self.expected.append('"fin"')
            if submetodo == "identificador":
                self.expected.append('"id"')
            if submetodo == "tkn_colon":
                self.expected.append('":"')
            if submetodo == "tkn_closing_par":
                expected = ['")"', '","']
                for i in expected:
                    self.expected.append(i)                     
            if submetodo == "palabras_reservadas_identificador":
                expected = ['"booleano"', '"cadena"', '"caracter"', '"entero"', '"id"', '"real"']
                for i in expected:
                    self.expected.append(i)  
            if submetodo == "declaracion":
                expected = ['"arreglo"', '"booleano"', '"cadena"', '"caracter"', '"entero"', '"id"', '"real"', '"var"']
                for i in expected:
                    self.expected.append(i)



      
        token_actual = self.tokens[self.pos]
        lexema = token_actual[0]
        if self.reservadas() or self.tokens[self.pos][0] in ['tkn_comma', 'tkn_assign', 'tkn_opening_par', 'tkn_opening_bra', 'tkn_closing_bra', 'tkn_closing_par', 'tkn_period',
         'tkn_colon', 'tkn_plus', 'tkn_minus', 'tkn_times', 'tkn_div', 'tkn_power', 'tkn_neq', 'tkn_leq', 'tkn_less', 'tkn_geq', 'tkn_greater', 'tkn_equal', 'newline']:
            
            
            if token_actual[0] == 'tkn_comma':
                lexema = ','
            if token_actual[0] == 'tkn_assign':
                lexema = '<-'
            if token_actual[0] == 'tkn_opening_par':
                lexema = '('
            if token_actual[0] == 'tkn_opening_bra':
                lexema = '['
            if token_actual[0] == 'tkn_closing_bra':
                lexema = ']'
            if token_actual[0] == 'tkn_closing_par':
                lexema = ')'
            if token_actual[0] == 'tkn_period':
                lexema = '.'
            if token_actual[0] == 'tkn_colon':
                lexema = ':'
            if token_actual[0] == 'tkn_plus':
                lexema = '+'
            if token_actual[0] == 'tkn_minus':
                lexema = '-'
            if token_actual[0] == 'tkn_times':
                lexema = '*'
            if token_actual[0] == 'tkn_div':
                lexema = '/'
            if token_actual[0] == 'tkn_power':
                lexema = '^'
            if token_actual[0] == 'tkn_neq':
                lexema = '<>'
            if token_actual[0] == 'tkn_leq':
                lexema = '<='
            if token_actual[0] == 'tkn_less':
                lexema = '<'
            if token_actual[0] == 'tkn_geq':
                lexema = '>='                                                                                                                                
            if token_actual[0] == 'tkn_greater':
                lexema = '>'
            if token_actual[0] == 'tkn_equal':
                lexema = '=' 
            if token_actual[0] == 'EOF':
                lexema = 'final de archivo'               
            fila, columna = token_actual[1], token_actual[2]
            mensaje = f"<{fila}:{columna}> Error sintactico: se encontro: \"{lexema}\"; se esperaba: {', '.join(self.expected)}."
        else:
            lexema = token_actual[1]
            fila, columna = token_actual[2], token_actual[3]
            mensaje = f"<{fila}:{columna}> Error sintactico: se encontro: \"{lexema}\"; se esperaba: {', '.join(self.expected)}."
        print(mensaje,end="")
        exit()

    def programa(self):
        
        if self.sentencia():
            if self.programa_Funcion():
                if self.tokens[self.pos][0] == 'EOF':
                    return True
                self.error("programa", "EOF")            
        return False

    def programa_Funcion(self):
        if self.EoL():
            if self.programa():
                return True
        if self.programa():
                return True
        return True

    def sentencia(self):  
        if self.declaracion():
            return True              
        if self.bloque_programa():
            return True            
        if self.EoL():
            return True                     
        if self.funcion():
            return True                           
        if self.procedimiento():
            return True          
        if self.registro():
            return True     
        if self.tokens[self.pos][0] == 'EOF':
            return False 
        pos = self.pos       
        if self.sentencia_acciones(False):
            self.pos = pos 
            self.error("sentencia", "conjunto") 
        self.error("sentencia", "sentencia_acciones")                
        return False

    def sentencia_acciones(self, nousable): 
        
        if nousable == "self.EoL()":
            return False
        if self.EoL():
            return True
        if nousable == "self.asignacion()":            
            return False    
        if self.asignacion():
            return True 
        if nousable == "self.lectura()":            
            return False    
        if self.lectura():
            return True 
        if nousable == "self.escritura()":            
            return False    
        if self.escritura():
            return True  
        if nousable == "self.condicional()":            
            return False    
        if self.condicional():
            return True 
        if nousable == "self.casos()":            
            return False    
        if self.casos():
            return True  
        if nousable == "self.mientras()":            
            return False    
        if self.mientras():
            return True 
        if nousable == "self.repita()":            
            return False     
        if self.repita():
            return True 
        if nousable == "self.para()":            
            return False       
        if self.para():
            return True 
        if nousable == "self.llamar()":            
            return False     
        if self.llamar():
            return True  
        if nousable == "self.retorne()":            
            return False    
        if self.retorne():
            return True
        return False

    def retorne(self):
        if self.tokens[self.pos][0] == 'retorne':
            self.pos += 1 
            if self.retorne_Ciclo():
                if self.EoL():
                    return True
                self.error("retorne", "EoL")                  
        return False

    def retorne_Ciclo(self):
        if self.identificador():
            if self.token():
                if self.palabras_reservadas() or self.token() or self.identificador():
                    if self.retorne_Ciclo():
                        return True                      
        if self.identificador():
            if self.retorne_Ciclo():
                return True
        if self.token():
            if self.retorne_Ciclo():
                return True
        if self.palabras_reservadas():
            if self.retorne_Ciclo():
                return True
        return True         
        
    def llamar(self):
        if self.tokens[self.pos][0] == 'llamar':
            self.pos += 1            
            if self.llamar_procedimiento():
                return True                    
        return False                

    def llamar_procedimiento(self):           
        if self.EoL():
            return True   
        if self.identificador():
            if self.expresion():
                return True
            self.error("llamar", "llamar_procedimiento_expresion") 
        self.error("llamar", "llamar_procedimiento_id") 
        return True            

    def declaracion(self): 
        
        if (self.tokens[self.pos][0] == 'cadena') and (self.tokens[self.pos+1][0] == 'tkn_opening_bra'):   
            self.pos += 1  
            if self.tokens[self.pos][0] == 'tkn_opening_bra':
                self.pos += 1
                if self.tokens[self.pos][0] == 'tkn_integer':
                    self.pos += 1
                    if self.tokens[self.pos][0] == 'tkn_closing_bra':
                        self.pos += 1            
                        if self.identificador():
                            if self.cadena_MULT_id():
                                return True
                        self.error("declaracion_cadena", "identificador") 
                    self.error("declaracion_cadena", "tkn_closing_bra")  
                self.error("declaracion_cadena", "tkn_integer")             
            self.error("declaracion_cadena", "tkn_opening_bra") 
        if (self.tokens[self.pos][0] == 'arreglo'):   
            self.pos += 1  
            if self.tokens[self.pos][0] == 'tkn_opening_bra':
                self.pos += 1
                if self.declaracion_arreglo():
                    if self.tokens[self.pos][0] == 'tkn_closing_bra':
                        self.pos += 1                                  
                        if self.tokens[self.pos][0] == 'de':
                            self.pos += 1                                      
                            if self.tipo_de_dato_declaracion():
                                if self.identificador():
                                    return True
                                self.error("declaracion_arreglo", "identificador") 
                            self.error("declaracion_arreglo", "tipo_de_dato") 
                        self.error("declaracion_arreglo", "de") 
                    self.error("declaracion_arreglo", "tkn_closing_bra")             
            self.error("declaracion_arreglo", "tkn_opening_bra") 
        if self.tokens[self.pos][0] == 'cadena': 
            self.pos += 1                
            if self.identificador():
                if self.declaracion_Ciclo():                        
                    return True  
            self.error("declaracion", "identificador") 
        if self.tokens[self.pos][0] == 'var':             
            self.pos += 1                            
            if self.tipo_de_dato_declaracion():
                if self.identificador():                       
                        return True  
                self.error("declaracion", "identificador") 
            self.error("declaracion", "tipo_de_dato")

        if self.tipo_de_dato():    
            if self.identificador():
                if self.declaracion_Ciclo():                        
                    return True  
            self.error("declaracion", "identificador") 
        if self.identificador():    
            if self.identificador():
                if self.declaracion_Ciclo():                        
                    return True  
            self.error("declaracion", "identificador") 
        return False
    
    def cadena_MULT_id(self):        
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            if self.identificador():
                if self.cadena_MULT_id():
                    return True
            self.error("asignacion", "identificador") 
        return True      

    def tipo_de_dato_declaracion(self):
        if self.tipo_de_dato():
            return True          
        if (self.tokens[self.pos][0] == 'cadena') and (self.tokens[self.pos+1][0] == 'tkn_opening_bra'):   
            self.pos += 1  
            if self.tokens[self.pos][0] == 'tkn_opening_bra':
                self.pos += 1
                if self.tokens[self.pos][0] == 'tkn_integer':
                    self.pos += 1
                    if self.tokens[self.pos][0] == 'tkn_closing_bra':
                        self.pos += 1  
                        return True 
                    self.error("declaracion_cadena", "tkn_closing_bra")  
                self.error("declaracion_cadena", "tkn_integer")             
            self.error("declaracion_cadena", "tkn_opening_bra") 
        if (self.tokens[self.pos][0] == 'arreglo'):   
            self.pos += 1  
            if self.tokens[self.pos][0] == 'tkn_opening_bra':
                self.pos += 1
                if self.declaracion_arreglo():
                    if self.tokens[self.pos][0] == 'tkn_closing_bra': 
                        self.pos += 1
                        return True 
                    self.error("declaracion_arreglo", "tkn_closing_bra")             
            self.error("declaracion_arreglo", "tkn_opening_bra")
        return False

    def declaracion_arreglo(self):       
        if self.tokens[self.pos][0] == 'tkn_integer':
            self.pos += 1
            if self.declaracion_arreglo_multiple():
                return True              
        self.error("declaracion_arreglo", "tkn_integer") 
        return False

    def declaracion_arreglo_multiple(self): 
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            if self.tokens[self.pos][0] == 'tkn_integer':
                self.pos += 1
                if self.declaracion_arreglo_multiple():
                    return True         
        return True

    def declaracion_Ciclo(self):
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            if self.EoL():
                if self.declaracion_Ciclo2():
                    return True      
        return True

    def declaracion_Ciclo2(self):
        if self.palabras_reservadas():
            if self.identificador():
                return True
            self.error("declaracion", "identificador")  
        if self.identificador():
            return True 
        self.error("declaracion", "identificador")    
        return False

    def asignacion(self):             
        if self.asignacionid():
            if self.tokens[self.pos][0] == 'tkn_assign':
                self.pos += 1                
                if self.expresion():
                    if self.funcion_Ciclo_EoL():
                        return True
                    self.error("asignacion", "EoL")   
                self.error("asignacion", "expresion")            
            self.error("asignacion", "tkn_assign") 
        return False

    def asignacionid(self):
        if self.identificador():
            if self.asignacionid_multiple():
                return True
            self.pos -= 1 
        if self.identificador():
            if self.asignacionid_arreglos():
                return True
            self.pos -= 1
        if self.identificador():
            if self.asignacionid_registros():
                return True
            self.pos -= 1
        if self.identificador():
            return True  
        return False 

    def asignacionid_registros(self):
        if self.tokens[self.pos][0] == 'tkn_period':
            self.pos += 1
            if self.identificador():
                return True
            self.error("asignacion", "identificador") 
        return False       

    def asignacionid_arreglos(self):
        if self.tokens[self.pos][0] == 'tkn_opening_bra':
            self.pos += 1
            if self.tipoDato_asignacion():    
                if self.tokens[self.pos][0] == 'tkn_closing_bra':
                    self.pos += 1 
                    return True
                self.error("asignacion", "tkn_closing_bra")                  
        return False 

    def tipoDato_asignacion(self):      
        if self.tokens[self.pos][0] == 'tkn_integer':
            self.pos += 1
            if self.declaracion_arreglo_multiple():
                return True  
        if self.identificador(): 
            return True                    
        self.error("asignacion", "tipoDato_asignacion") 
        return False

    def tipoDato_asignacion_multiple(self): 
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            if self.tokens[self.pos][0] == 'tkn_integer':
                self.pos += 1
                if self.declaracion_arreglo_multiple():
                    return True         
        return True                 
          
    def asignacionid_multiple(self):
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1            
            if self.identificador():
                if asignacionid_multiple():
                    return True
            self.error("asignacion", "identificador") 
        return False      

    def lectura(self):   
        
        if self.tokens[self.pos][0] == 'lea':
            self.pos += 1            
            if self.lectura_Ciclo():
                if self.EoL():
                    return True
                self.error("lectura", "EoL")    
        return False

    def lectura_Ciclo(self):
        
        if self.identificador():
            if self.lectura_multiple():
                return True                               
        self.pos -= 1               
        if self.identificador():
            if self.lectura_multiple_Metodos():
                return True                
        self.pos -= 1        
        if self.identificador():
            return True
        
        self.pos += 2     
        self.error("lectura", "identificador")                             
        return False

    def lectura_multiple(self):  
               
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1    
                   
            if self.identificador():
                
                if self.lectura_multiple():
                    return True
            self.error("lectura_multiple", "identificador") 
         
        return True   

    def lectura_multiple_Metodos(self):
        if self.tokens[self.pos][0] == 'tkn_period':
            self.pos += 1            
            if self.identificador():
                return True
            self.error("lectura_multiple", "identificador")  
        return True         

    def escritura(self):        
        if self.tokens[self.pos][0] == 'escriba':
            self.pos +=1
            if self.escritura_Ciclo():
                if self.EoL():
                    return True
                self.error("escritura", "EoL")                  
        return False

    def escritura_Ciclo(self):
        if self.identificador():
            if self.token():
                if self.token() or self.identificador():
                    if self.escritura_Ciclo():
                        return True
                self.error("escritura", "palabras_reservadas")             
        if self.identificador():
            if self.escritura_Ciclo():
                return True
        if self.token():
            if self.escritura_Ciclo():
                return True
        if(self.tokens[self.pos][0] == 'newline'):
            return True
        else:
            self.error("escritura", "palabras_reservadas")  

    def escritura_Ciclo_EoL(self):   
        if self.EoL():
            if self.escritura_Ciclo_EoL():
                return True
        return True

    def identificador(self):
        if self.tokens[self.pos][0] == 'id':
            self.pos += 1
            return True           
        return False

    def expresion(self):
        self.abiertos = 0
        self.cerrados = 0
        if self.expresion_Ciclo():            
            if self.abiertos != self.cerrados:
                self.error("expresion", "parentesis")   
                return False
            return True 
        return False

    def expresion_Ciclo(self):
        if self.factor_expresion():
            if self.expresion_Ciclo():
                return True
        return True

    def factor_expresion(self):
        if((self.tokens[self.pos][0] == 'tkn_opening_par') or (self.tokens[self.pos][0] == 'tkn_opening_bra')):
            self.abiertos +=1
        if((self.tokens[self.pos][0] == 'tkn_closing_bra') or (self.tokens[self.pos][0] == 'tkn_closing_par')):
            self.cerrados +=1
        if self.token():            
            return True
        if self.identificador():
            return True   
        if self.palabras_reservadas():          
            return True
        return False

    def tipo_de_dato(self)    :
        if self.tokens[self.pos][0] == 'booleano':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'caracter':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'entero':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'real':
            self.pos += 1
            return True  

    def palabras_reservadas(self):
        if self.tokens[self.pos][0] == 'booleano':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'caracter':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'div':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'entero':
            self.pos += 1
            return True           
        if self.tokens[self.pos][0] == 'falso':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'mod':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'o':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'real':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'retorne':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'var':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'verdadero':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'y':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'llamar':
            self.pos += 1
            return True            
        return False

    def EoL(self):
        if self.tokens[self.pos][0] == 'newline':
            self.pos += 1
            return True
        return False

    def token(self):
        if self.tokens[self.pos][0] == 'tkn_assign':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_char':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_closing_bra':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_closing_par':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_colon':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_div':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_equal':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_geq':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_greater':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_integer':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_leq':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_less':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_minus':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_opening_bra':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_opening_par':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_period':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_plus':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_power':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_real':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_str':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_times':
            self.pos += 1
            return True
        if self.tokens[self.pos][0] == 'tkn_neq':
            self.pos += 1
            return True
        return False

    def condicional(self):
        if self.tokens[self.pos][0] == 'si':
            self.pos += 1
            if self.expresion():
                if self.tokens[self.pos][0] == 'entonces':
                    self.pos += 1
                    if self.EoL():
                        if self.sentencia_condicional():
                            if self.tokens[self.pos][0] == 'fin si':
                                self.pos += 1
                                return True
                            self.error("condicional", "fin_si")     
                        self.error("condicional", "sentencia_condicional")         
                self.error("condicional", "entonces")            
            self.error("condicional", "expresion")                            
        return False

    def sentencia_condicional(self):
        if self.acciones_condicional():
            if self.sentencia_condicional_Sino():
                return True               
        if self.acciones_condicional():
            return True
        return False

    def acciones_condicional(self):
        if self.sentencia_acciones(False):
            if self.acciones_condicional():
                return True
        return True

    def sentencia_condicional_Sino(self):
        if self.tokens[self.pos][0] == 'sino':
            self.pos += 1
            if self.acciones_condicional():
                return True
        return False

    def casos(self):
        if self.tokens[self.pos][0] == 'caso':
            self.pos += 1
            if self.identificador():
                if self.EoL():
                    if self.bloque_codigo_caso():
                        if self.tokens[self.pos][0] == 'sino':
                            self.pos += 1
                            if self.tokens[self.pos][0] == 'tkn_colon':
                                self.pos += 1
                                if self.EoL():
                                    if self.bloque_codigo_caso_sino():
                                        if self.EoL():
                                            if self.tokens[self.pos][0] == 'fin caso':
                                                self.pos += 1
                                                return True
                                            self.error("casos", "fin_caso")              
                            self.error("casos", "tkn_colon")
                        self.error("casos", "sino")                                         
        return False

    def valor_caso(self):        
        if self.tokens[self.pos][0] == 'tkn_integer':
            self.pos += 1
            if self.tokens[self.pos+1][0] == 'tkn_comma' or self.tokens[self.pos+1][0] == 'tkn_colon':
                if self.valor_caso_tail():
                    return True  
            self.error("casos", "tkn_comma_tkn_colon")    
        return False

    def valor_caso_tail(self):
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            if self.tokens[self.pos][0] == 'tkn_integer':
                self.pos += 1
                if self.valor_caso_tail():
                    return True
            self.error("casos", "tkn_integer") 
        return True

    def bloque_codigo_caso(self):
        if self.valor_caso():
            if self.tokens[self.pos][0] == 'tkn_colon':
                self.pos += 1
                if self.EoL():
                    if self.sentencia_acciones(False):                        
                        if self.bloque_codigo_caso():
                            return True                        
        return True

    def bloque_codigo_caso_sino(self):
        if self.sentencia_acciones(False):                        
            if self.bloque_codigo_caso():
                return True                        
        return True        

    def mientras(self):        
        if self.tokens[self.pos][0] == 'mientras':
            self.pos += 1
            if self.expresion():
                if self.tokens[self.pos][0] == 'haga':
                    self.pos += 1
                    if self.EoL():
                        if self.ciclo_mientras():
                            if self.tokens[self.pos][0] == 'fin mientras':
                                self.pos += 1
                                return True
                            self.error("mientras", "fin mientras")        
                self.error("mientras", "haga") 
            self.error("mientras", "expresion")                 
        return False

    def ciclo_mientras(self):
        if self.sentencia_acciones(False):
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
                    self.error("repita", "expresion")    
                self.error("repita", "hasta") 
        return False

    def ciclo_repita(self):
        if self.sentencia_acciones(False):
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
                                self.error("para", "fin_para")
                        self.error("para", "haga")
                    self.error("para", "expresion")
                self.error("para", "hasta")
            self.error("para", "expresion")
        return False

    def ciclo_para(self):
        if self.sentencia_acciones(False):
            if self.ciclo_para():
                return True
        return True    

    def procedimiento(self):
        if self.tokens[self.pos][0] == 'procedimiento':
            self.pos += 1
            if self.identificador():                
                if self.procedimiento_Ciclo_EoL():                         
                    if self.parametros_procedimiento():
                        if self.procedimiento_Ciclo_EoL(): 
                            if self.tokens[self.pos][0] == 'inicio':
                                self.pos += 1 
                                if self.procedimiento_Ciclo_EoL():                          
                                    if self.procedimiento_Ciclo():                                    
                                        if self.tokens[self.pos][0] == 'fin':
                                            self.pos += 1
                                            return True  
                                        self.error("procedimiento", "fin")                  
                            self.error("procedimiento", "inicio")  
                    self.error("procedimiento", "parametros_procedimiento")
            self.error("procedimiento", "identificador") 
        return False



    def parametros_procedimiento(self):
        if self.tokens[self.pos][0] == 'tkn_opening_par':
            self.pos += 1
                      
            if self.declaracion():
                
                if self.MULT_parametros_procedimiento():
                    if self.tokens[self.pos][0] == 'tkn_closing_par':
                        self.pos += 1
                        return True
                    self.error("funcion", "tkn_closing_par")   
            self.error("funcion", "declaracion")

        if self.declaracion():
            return True   
        if self.funcion_Ciclo_EoL(): 
            return True                             
        return True


    def MULT_parametros_procedimiento(self):
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            if self.declaracion():
                if self.MULT_parametros_ciclo_funcion():
                    return True
        return True



    def procedimiento_Ciclo(self):
        
        if self.tokens[self.pos][0] == 'retorne':
            self.error("procedimiento", "procedimiento_Ciclo")
            return False
        if self.sentencia_acciones(False):
            if self.procedimiento_Ciclo():
                return True
        return True     

    def procedimiento_Ciclo_EoL(self):  
        if self.EoL():
            if self.funcion_Ciclo_EoL():
                return True
        return True    

    def funcion(self):   
        if self.tokens[self.pos][0] == 'funcion':
            self.pos += 1        
            if self.identificador():    
                if self.funcion_Ciclo():                          
                    if self.tokens[self.pos][0] == 'inicio':
                        self.pos += 1
                        if self.EoL():
                            if self.acciones_funcion():                            
                                if self.tokens[self.pos][0] == 'fin':
                                    self.pos += 1                                  
                                    return True
                                self.error("funcion", "fin")
                    self.error("funcion", "inicio")            
            self.error("funcion", "identificador")            
        return False

    def funcion_Ciclo(self):
        if self.parametros_ciclo_funcion():
            if self.tokens[self.pos][0] == 'tkn_colon':
                self.pos += 1
                if self.palabras_reservadas():
                    if self.funcion_Ciclo_EoL():
                        return True
                if self.identificador():
                    if self.funcion_Ciclo_EoL():
                        return True
                if (self.tokens[self.pos][0] == 'cadena') and (self.tokens[self.pos+1][0] == 'tkn_opening_bra'):   
                    self.pos += 1  
                    if self.tokens[self.pos][0] == 'tkn_opening_bra':
                        self.pos += 1
                        if self.tokens[self.pos][0] == 'tkn_integer':
                            self.pos += 1
                            if self.tokens[self.pos][0] == 'tkn_closing_bra':
                                self.pos += 1  
                                if self.funcion_Ciclo_EoL(): 
                                    return True  
                            self.error("funcion", "tkn_closing_bra")  
                        self.error("funcion", "tkn_integer")             
                    self.error("funcion", "tkn_opening_bra")        
                self.error("funcion", "palabras_reservadas_identificador")     
            self.error("funcion", "tkn_colon")     
        return False

    def funcion_Ciclo_EoL(self):    
        if self.EoL():
            if self.funcion_Ciclo_EoL():
                return True
        return True

    def parametros_ciclo_funcion(self):
        if self.tokens[self.pos][0] == 'tkn_opening_par':
            self.pos += 1
            if self.declaracion():
                if self.MULT_parametros_ciclo_funcion():
                    if self.tokens[self.pos][0] == 'tkn_closing_par':
                        self.pos += 1
                        return True
                    self.error("funcion", "tkn_closing_par")   
            self.error("funcion", "declaracion")

        if self.declaracion():
            return True   
        if self.funcion_Ciclo_EoL(): 
            return True                             
        return True


    def MULT_parametros_ciclo_funcion(self):
        if self.tokens[self.pos][0] == 'tkn_comma':
            self.pos += 1
            if self.declaracion():
                if self.MULT_parametros_ciclo_funcion():
                    return True
        return True

    def acciones_funcion(self):
        if self.sentencia_acciones(False):
            if self.EoL():
                if self.acciones_funcion():
                    return True
        return True  


    def registro(self):
        if self.tokens[self.pos][0] == 'registro':
            self.pos += 1
            if self.identificador():
                if self.EoL():
                    if self.registro_Ciclo():                       
                        if self.tokens[self.pos][0] == 'fin registro':
                            self.pos += 1
                            return True
                        self.error("registro", "fin registro") 
            self.error("registro", "identificador")            
        return False

    def registro_Ciclo(self):
        if self.declaracion():
            if self.EoL():
                if self.registro_Ciclo():
                    return True       
        return True

   
    def bloque_programa(self):
        if self.tokens[self.pos][0] == 'inicio':
            self.pos += 1
            if self.bloque_programa_Ciclo():
                if self.tokens[self.pos][0] == 'fin':
                    self.pos += 1
                    return True
                self.error("bloque_programa", "fin")    
        return False

    def bloque_programa_Ciclo(self):
        
        if self.sentencia_acciones(False):
            if self.bloque_programa_Ciclo():
                return True
        return True

    def analizar(self):
        if self.programa():          	
            print("El analisis sintactico ha finalizado exitosamente.",end="")


if __name__ == "__main__":

    #s = sys.stdin.read()

    s='''funcion pi(var entero a ,real b,cadena [10] my_string entero id):

// ups, me falto la coma antes de declarar otro parámetro :'v'''

    i = 0
    fraselexica = []
    entrada = []

    for i in analizador_lexico(s):
        fraselexica.append(i)

    for i in range (len(fraselexica)):
        entrada.append(fraselexica[i].strip("<>").split(','))
        #print(entrada[i])
        
    analizador = AnalizadorSintactico(entrada)
    analizador.analizar()
