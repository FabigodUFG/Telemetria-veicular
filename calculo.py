def cal_aceleracao(prev_velocidade, velocidade, delta_tempo):

    aceleracao = (velocidade - prev_velocidade) / delta_tempo 
    return aceleracao

def cal_distancia_total(prev_velocidade, velocidade_atual, delta_tempo, tolerancia=0.1):
    # Ignora o cálculo se a velocidade média estiver próxima de zero
    velocidade_media = (prev_velocidade + velocidade_atual) / 2
    if abs(velocidade_media) < tolerancia:
        return 0  # Não adiciona distância
    
    # Calcula a distância percorrida nesse intervalo
    distancia = velocidade_media * delta_tempo
    return distancia

def cal_consumo(distancia_total, combustivel_inicial, combustivel_atual):    
    # Cálculo do combustível consumido até agora
    consumo_total = combustivel_inicial - combustivel_atual

    # Consumo em km/L (apenas calcula se já teve algum gasto)
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