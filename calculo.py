def cal_aceleracao(prev_velocidade, velocidade, tempo):
    #print(f"pre_velocidade: {prev_velocidade}")
    #print(f"velocidade: {vel}")

    aceleracao = (velocidade - prev_velocidade) / tempo 
    #print(f"Aceleração: {aceleracao} m/s²")
    return aceleracao

def cal_distancia_total(prev_velocidade, velocidade_atual, delta_time, tolerancia=0.1):
    # Ignora o cálculo se a velocidade média estiver próxima de zero
    velocidade_media = (prev_velocidade + velocidade_atual) / 2
    if abs(velocidade_media) < tolerancia:
        return 0  # Não adiciona distância
    
    # Calcula a distância percorrida nesse intervalo
    distancia = velocidade_media * delta_time
    return distancia

def cal_consumo(distancia_total, combustivel_inicial, combustivel):    
    # Cálculo do combustível consumido até agora
    consumo_total = combustivel_inicial - combustivel

    # Consumo em km/L (apenas calcula se já percorreu alguma distância)
    if consumo_total > 0:
        consumo = (distancia_total / 1000) / (consumo_total / 1000)  # Distância em km / Litros consumidos
    else:
        consumo = 0  # Caso ainda não tenha consumido combustível

    return consumo

def cal_vmed(vetor_v, contador_i):
    vmed = vetor_v / contador_i
    return vmed

def cal_tmed(vetor_t, contador_j):
    tmed = vetor_t / contador_j
    return tmed