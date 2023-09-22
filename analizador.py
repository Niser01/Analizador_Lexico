from typing import NamedTuple
import re
import sys

class Token(NamedTuple):
    token_type: str
    token_value: str
    line: int
    column: int

def analizador_lexico(frase):

    palabras_reservadas = {'inicio', 'fin', 'entero', 'real', 'booleano', 'caracter', 'cadena', 'verdadero', 'falso', 'escriba', 'lea', 'llamar',
        'si', 'sino', 'y', 'o', 'mod', 'caso', 'mientras', 'haga', 'repita', 'hasta', 'para', 'procedimiento', 'var', 'retorne', 'funcion', 'nueva_linea',
        'registro', 'arreglo', 'de', 'entonces',     
        }
    tokens = [
        ('one_line_comment', r'\/\/.*'),
        ('multi_line_comment', r'[/]+[*].*[*]+[/]'), 
        ('tkn_real', r'\d+(\.\d*)?'),    
        ('tkn_assign', r'<-'),                      
        ('id', r'[A-Za-z_0-9]+'),    
        ('tkn_str', r'"([^"]*)"'),   
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
        ('tkn_char', r"['\w']+"), 
        ('skip', r'[ \t]+'), 
        ('newline', r'\n'),
        ('NiF', r'.'),
        
    ]
    
    generadorPatrones = '|'.join('(?P<%s>%s)' % pair for pair in tokens)
    line_num = 1 
    line_start = 0

    for mo in re.finditer(generadorPatrones, frase):
        token_type = mo.lastgroup
        token_value = mo.group()
        column = (mo.start()+1) - line_start
        
        if(token_type == 'id'):
            token_value = token_value.lower()
            if(token_value in palabras_reservadas):
                token_type=token_value
                print(f"<{token_value},{line_num},{column}>")
                continue
            print(f"<{token_type},{token_value},{line_num},{column}>")
            continue
        
        elif token_type == 'newline':
            line_start = mo.end()
            line_num += 1
            continue
        elif token_type == 'skip':
            continue
        elif token_type == 'NiF':
            print(f'>>> Error lexico (linea: {line_num}, posicion: {column})')
            return None
        else:
            if(token_type == 'tkn_char'):
                print(f"<{token_type},{token_value[1]},{line_num},{column}>")
                continue
            if(token_type == 'tkn_str'):
                n=len(token_value)
                print(f"<{token_type},{token_value[1:(n-1)]},{line_num},{column}>")
                continue
            if(token_type == 'tkn_real'):
                if('.' in token_value):
                    print(f"<{token_type},{token_value},{line_num},{column}>")
                    continue
                else:
                    token_type = 'tkn_integer'
                    print(f"<{token_type},{token_value},{line_num},{column}>")
                    continue
            if(token_type == 'one_line_comment' or token_type == 'multi_line_comment'):
                continue
            print(f"<{token_type},{line_num},{column}>")
            continue
        yield Token(token_type, token_value, line_num, column)  


if __name__ == "__main__":



    s = sys.stdin.read()
   
    for token in analizador_lexico(s):
        print(token)
  

