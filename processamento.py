import re

# Variáveis globais para armazenar os valores anteriores
prev_velocidade = None
prev_combustivel = None
prev_temperatura = None
prev_marcha = None

def processar_dados(leitura):
    #global prev_velocidade, prev_combustivel, prev_temperatura, prev_marcha
    
    # Remover os símbolos de maior e menor
    leitura = leitura.strip('<>')

    # Usando regex para separar os dados com base no '#', agora permitindo números negativos
    pattern = r"(-?\d+\.?\d*)#(-?\d+\.?\d*)#(-?\d+\.?\d*)#(-?\d+)"
    match = re.match(pattern, leitura)
    
    if not match:
        print("Leitura inválida")
        return
    
    # Extraindo valores da leitura
    velocidade = float(match.group(1))
    combustivel = float(match.group(2))
    temperatura = float(match.group(3))
    marcha = int(match.group(4))

    # Retorna os valores para comparação na main
    return velocidade, combustivel, temperatura, marcha