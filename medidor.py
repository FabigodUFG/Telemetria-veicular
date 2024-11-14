import plotly.graph_objects as go
import plotly.io as pio
import io

cor_de_fundo = '#f0f0f0'

def plot_image_velocidade(velocidade):
    # Criar figura para a velocidade
    fig_velocidade = go.Figure()
    fig_velocidade.add_trace(go.Indicator(
        mode="gauge+number",
        value=velocidade,
        title={"text": "<b>Velocidade</b>"},
        gauge={"axis": {"range": [None, 160]},
               "steps": [{"range": [0, 160], "color": "lightgrey"}],
               "threshold": {"line": {"color": "red", "width": 4},
                             "thickness": 1, "value": 160}},
        number={'suffix': " Km/h"},
    ))

    fig_velocidade.update_layout(
        plot_bgcolor=cor_de_fundo,
        paper_bgcolor=cor_de_fundo
    )

    # Converter o gráfico em imagem PNG no buffer
    buffer_velocidade = io.BytesIO()
    pio.write_image(fig_velocidade, buffer_velocidade, format='png')
    buffer_velocidade.seek(0)  # Voltar ao início do buffer
    return buffer_velocidade

###################################################################################################

def plot_image_combustivel(combustivel):
    # Criar figura para o combustível
    fig_combustivel = go.Figure()
    fig_combustivel.add_trace(go.Indicator(
        mode="gauge",
        value=combustivel,
        domain={'x': [0, 1], 'y': [0.1, 0.6]},
        gauge={
            'shape': "bullet",
            'axis': {'range': [None, 3000]},
            'steps': [{'range': [0, 1000], 'color': "lightgray"},
                      {'range': [1000, 2000], 'color': "gray"}],
            'bar': {'color': "darkblue"}
        }
    ))

    fig_combustivel.add_annotation(
        text="<b>Combustível</b>",
        x=0,
        y=0.7,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=23)
    )

    fig_combustivel.update_layout(
        plot_bgcolor=cor_de_fundo,
        paper_bgcolor=cor_de_fundo
    )

    # Converter o gráfico de combustível em imagem PNG no buffer
    buffer_combustivel = io.BytesIO()
    pio.write_image(fig_combustivel, buffer_combustivel, format='png')
    buffer_combustivel.seek(0)
    return buffer_combustivel

###################################################################################################

def plot_image_temperatura(temperatura):
    # Criar figura para a temperatura
    fig_temperatura = go.Figure()
    fig_temperatura.add_trace(go.Indicator(
        mode="gauge",
        value=temperatura,
        domain={'x': [0, 1], 'y': [0.1, 0.5]},
        gauge={
            'shape': "bullet",
            'axis': {'range': [None, 200]},
            'steps': [{'range': [0, 170], 'color': "lightgray"},
                      {'range': [170, 200], 'color': "darkred"}],
            'bar': {'color': "darkblue"}
        }
    ))

    fig_temperatura.add_annotation(
        text="<b>Temperatura</b>",
        x=0,
        y=0.6,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=23)
    )

    fig_temperatura.update_layout(
        plot_bgcolor=cor_de_fundo,
        paper_bgcolor=cor_de_fundo
    )

    # Converter o gráfico de temperatura em imagem PNG no buffer
    buffer_temperatura = io.BytesIO()
    pio.write_image(fig_temperatura, buffer_temperatura, format='png')
    buffer_temperatura.seek(0)
    return buffer_temperatura

###################################################################################################

def plot_image_marcha(marcha):
    
    # Lógica da marcha
    if marcha == 0:
        ajuste = "N"
        cor = "red"
    else:
        ajuste = "N"
        cor = "verde"

    """
    elif marcha == -1:
        ajuste = "R"
        cor = "yellow"
    else:
        ajuste = str(marcha)
        cor = "green"
    """

    marcha = ajuste

    # Criar figura para a marcha
    fig_marcha = go.Figure()
    fig_marcha.add_shape(type="circle",
                        xref="paper", yref="paper",
                        x0=0.4, x1=0.6, y0=0.3, y1=0.633,
                        line_color="grey",
                        fillcolor=cor,
                        line_width=5
                        )

    # Adiciona o texto no meio do círculo
    fig_marcha.add_annotation(text=marcha,
                             xref="paper", yref="paper",
                             x=0.5, y=0.466,
                             showarrow=False,
                             font=dict(size=50, color="black")
                             )

    fig_marcha.update_layout(
        xaxis=dict(visible=False),  # Remove o eixo X
        yaxis=dict(visible=False),  # Remove o eixo Y
        plot_bgcolor=cor_de_fundo,
        paper_bgcolor=cor_de_fundo
    )

    buffer_marcha = io.BytesIO()
    pio.write_image(fig_marcha, buffer_marcha, format='png')
    buffer_marcha.seek(0)
    return buffer_marcha

###################################################################################################