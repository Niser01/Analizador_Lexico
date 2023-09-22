import re as re

def analizador_lexico(frase):
    # Como el lenguaje no discrimina entre mayusulas y minusculas, se pasa todo a minusculas para facilitar el proceso
    frase = frase.lower()
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
        'entonces',
        'tkn_period',     
        'tkn_comma',
        'tkn_colon', 
        'tkn_closing_bra',    
        'tkn_opening_bra',   
        'tkn_closing_par',   
        'tkn_opening_par',
        'tkn_plus',    
        'tkn_minus',   
        'tkn_times',   
        'tkn_div',    
        'tkn_power',    
        'tkn_equal',    
        'tkn_neq',     
        'tkn_less',     
        'tkn_leq',      
        'tkn_greater',     
        'tkn_geq', 
        'tkn_assign',       
        }
    tokens = [
        ('tkn_real',   r'\d+(\.\d*)?'), 
        ('tkn_integer',   r'[0-9]'),           
        ('tkn_assign',   r'<-'),                      
        ('id',       r'[A-Za-z_0-9]+'),    
        ('tkn_str',       r'["\w]+'),   
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
        ('tkn_char',       r"['\w']+"), 
        ('skip',     r'[ \t]+'), 
        ('newline',  r'\n'),
        ('NiF', r'.'),
    ]
    
    generadorPatrones = '|'.join('(?P<%s>%s)' % pair for pair in tokens)
    line_num = 1
    line_start = 0

    for mo in re.finditer(generadorPatrones, frase):
        token_type = mo.lastgroup
        token_value = mo.group()

        column = (mo.start()+1) - line_start
        if((token_type == 'id' and token_value in palabrasReservadas)):
            token_type=token_value
            print(f"<{token_value}, {line_num}, {column}>")
        elif (token_type in palabrasReservadas):
            print(f"<{token_type}, {line_num}, {column}>")
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
                print(f"<{token_type}, {token_value[1]}, {line_num}, {column}>")
                continue
            print(f"<{token_type}, {token_value}, {line_num}, {column}>")
         
    
    
        
        


if __name__ == "__main__":

    frase = '''my_Var1 <- 02
my_Var2 <- -3.145
string <- "Hello world" 
char <- 'a' '''
    for token in analizador_lexico(frase):
        print(token)
  

