

def analizador_sintactico(frase):
    return 0



if __name__ == "__main__":

    s = sys.stdin.read()

    for token in analizador_sintactico(s):
        print(token)
