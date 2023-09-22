import re as re

def analizador_lexico(frase):
    token_type: str
    token_value: str
    line: int
    column: int

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
        ('tkn_real',   r'\d+(\.\d*)?'), 
        ('tkn_integer',   r'[0-9]'),           
        ('tkn_assign',   r'<-'),                      
        ('id',       r'[A-Za-z]+'),    
        ('tkn_str',       r'\" + [A-Za-z] + \"'),   
        ('tkn_period',       r'\.'),      
        ('tkn_comma',       r'\,'), 
        ('tkn_colon',       r'\:'), 
        ('tkn_closing_bra',       r'\]'), 
        ('tkn_opening_bra',       r'\['), 
        ('tkn_closing_par',       r'\)'), 
        ('tkn_opening_par',       r'\('), 
        ('tkn_plus',       r'\+'), 
        ('tkn_minus',       r'\-'), 
        ('tkn_times',       r'\*'), 
        ('tkn_div',       r'\/'), 
        ('tkn_power',       r'\^'), 
        ('tkn_equal',       r'\='), 
        ('tkn_neq',       r'<>'), 
        ('tkn_less',       r'\<'), 
        ('tkn_leq',       r'<='), 
        ('tkn_greater',       r'\>'), 
        ('tkn_geq',       r'>='), 

    ]
    
    generadorPatrones = '|'.join('(?P<%s>%s)' % pair for pair in tokens)
    line_num = 1
    line_start = 0
    posicion = 0

    while posicion < len(frase):
        mo = re.finditer(generadorPatrones, frase)
        token_type = mo.lastgroup
        token_value = mo.group()
        column = (mo.start()+1) - line_start
        print(f"<{token_type}, {token_value}, {line_num}, {column}>")



if __name__ == "__main__":

    frase = '''lea entero o real

   y
 Escriba nueva_linea haga

   mientRAs repita

        Entonces'''
    for token in analizador_lexico(frase):
        print(token)
  

