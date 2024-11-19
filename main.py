import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import TclError

from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import time
import sys
import glob
import serial
import threading

from digi.xbee.devices import XBeeDevice

from calculo import *
from medidor import *           # Importa as funções do arquivo medidor.py
from processamento import *     # Importa as funções do arquivo processamento.py

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Telemetria")
        self.geometry("1550x820")  # Definindo a altura inicial

        # Frame para o cabeçalho (5 colunas)
        self.header_frame = tk.Frame(self)
        self.header_frame.grid(row=0, column=0, columnspan=5, sticky='nsew')

        # Adicionando colunas ao cabeçalho
        for i in range(5):
            self.header_frame.grid_columnconfigure(i, weight=1)

        # Valores zerados para iniciar o programa
        self.velocidade = 0
        self.combustivel = 0
        self.temperatura = 0
        self.marcha = 0
        self.aceleracao = 0

        # variáveis para calculos
        self.prev_velocidade = 0.0
        self.prev_combustivel = 0.0
        self.prev_temperatura = 0.0
        self.prev_marcha = 0
        self.prev_time = time.time()

        self.contador_i = 0
        self.contador_j = 0

        self.distancia_total = 0.0
        self.combustivel_inicial = None
        self.consumo = 0
        self.vetor_v = 0
        self.vmed = 0
        self.vetor_t = 0
        self.tmed = 0

        # Variáveis para o gráfico
        self.tempo = []
        self.velocidade_data = []
        self.tempo_inicial = time.time()
        self.after_id = None

        # Variável para guardas os ID's da tabela de dados
        self.itens_tabela = {}

        # Variaveis para a conexão
        self.baud_rate = 9600
        self.conectado = False  # Estado da conexão

        # Controle das threads
        self.thread_grafico = False

        self.setup_ui()
        self.create_graph()  # Criar o gráfico na interface
        self.update_graph()  # Desenha os instrumentos na tela quando inicia
        self.leitura_thread = None
        self.leitura_ativa = threading.Event()
        self.protocol("WM_DELETE_WINDOW", self.fechar_janela) # Função para fechar o programa sem erros

    ###################################################################################################

    def alternar_conexao(self):
        porta_selecionada = self.combobox.get()
        
        if not self.conectado:
            # Iniciar conexão
            if porta_selecionada and porta_selecionada != "Selecione uma porta":
                try:
                    self.dispositivo = XBeeDevice(porta_selecionada, self.baud_rate)
                    self.dispositivo.open()
                    print(f"Conectado ao XBee na porta {porta_selecionada} com baudrate {self.baud_rate}")
                    
                    self.botao_conectar.config(text="Desconectar", bg="red")
                    self.conectado = True
                    
                    # Inicia ou reutiliza a thread de leitura
                    self.leitura_ativa.set()  # Permite que a thread execute
                    if self.leitura_thread is None or not self.leitura_thread.is_alive():
                        self.leitura_thread = threading.Thread(target=self.ler_dados_xbee, daemon=True)
                        self.leitura_thread.start()

                except Exception as e:
                    print(f"Erro ao conectar: {e}")
                    messagebox.showerror("Erro", f"Falha na conexão: {e}")
                    self.desconectar()
            else:
                messagebox.showwarning("Aviso", "Por favor, selecione uma porta para conectar.")
        else:
            # Desconectar
            self.desconectar()
            self.reset_grafico()

    def ler_dados_xbee(self):
        try:
            while self.leitura_ativa.is_set():
                msg = self.dispositivo.read_data()
                if msg:
                    dados_recebidos = msg.data.decode('utf-8').strip()
                    print(f"Dado recebido: {dados_recebidos}")
                    dados_separados = processar_dados(dados_recebidos)
                    self.atualizar_dados(dados_separados)
                time.sleep(0.1)  # Evita uso excessivo de CPU

        except Exception as e:
            print(f"Erro na leitura do XBee: {e}")
        finally:
            self.desconectar()

    def desconectar(self):
        if self.conectado:
            self.conectado = False
            self.leitura_ativa.clear()  # Sinaliza para a thread encerrar
            if self.leitura_thread is not None:
                self.leitura_thread.join()  # Aguarda o término da thread
            try:
                self.dispositivo.close()
                print("Conexão com o XBee encerrada.")
            except Exception as e:
                print(f"Erro ao desconectar: {e}")
            finally:
                self.botao_conectar.config(text="Iniciar Conexão", bg="green")

    def atualizar_dados(self, dados):
        global prev_velocidade, prev_combustivel, prev_temperatura, prev_marcha

        if dados is None:  # Se os dados forem inválidos, não faz nada
            return
        
        velocidade, combustivel, temperatura, marcha = dados
        current_time = time.time()
        delta_time = current_time - self.prev_time

        # Inicializa o combustível inicial na primeira leitura
        if self.combustivel_inicial is None:
            self.combustivel_inicial = combustivel

        # Calcula aceleração e distância
        prev_velocidade = prev_velocidade if prev_velocidade is not None else 0
        self.aceleracao = cal_aceleracao(prev_velocidade, float(velocidade), delta_time)
        nova_distancia = cal_distancia_total(prev_velocidade, float(velocidade), delta_time)
        self.distancia_anterior = self.distancia_total
        self.distancia_total += nova_distancia

        if combustivel != prev_combustivel:

            self.consumo = cal_consumo(self.distancia_total, self.combustivel_inicial, combustivel)

        # Calcula médias de velocidade e temperatura
        self.contador_i += 1
        self.vetor_v += velocidade
        self.vmed = cal_vmed(self.vetor_v, self.contador_i)

        self.contador_j += 1
        self.vetor_t += temperatura
        self.tmed = cal_tmed(self.vetor_t, self.contador_j)

        self.prev_time = current_time

        # Funções de atualização usando threads
        def atualizar_dados_valores():
            # Atualiza apenas se houver diferença significativa
            if self.distancia_total != self.distancia_anterior:
                self.atualizar_valor_tabela("Distancia total", f"{self.distancia_total} metros")
                self.distancia_anterior = self.distancia_total
            self.atualizar_valor_tabela("Aceleração", f"{self.aceleracao} m/s²")
            self.atualizar_valor_tabela("Velocidade Média", f"{self.vmed} Km/h")
            self.atualizar_valor_tabela("Consumo", f"{self.consumo} Km/L")
            self.atualizar_valor_tabela("Temperatura Média", f"{self.tmed} °C")

        def atualizar_dados_velocidade():
            global prev_velocidade
            if velocidade != prev_velocidade:
                self.update_velocidade(velocidade)
                prev_velocidade = velocidade
            self.atualizar_grafico(velocidade)

        def atualizar_dados_combustivel():
            global prev_combustivel
            if combustivel != prev_combustivel:
                self.update_combustivel(combustivel)
                prev_combustivel = combustivel

        def atualizar_dados_temperatura():
            global prev_temperatura
            if temperatura != prev_temperatura:
                self.update_temperature(temperatura)
                prev_temperatura = temperatura

        def atualizar_dados_marcha():
            global prev_marcha
            if marcha != prev_marcha:
                self.update_marcha(marcha)
                prev_marcha = marcha

        atualizar_dados_valores()
        atualizar_dados_velocidade()
        atualizar_dados_combustivel()
        atualizar_dados_temperatura()
        atualizar_dados_marcha()

    ###################################################################################################

    def setup_ui(self):
        ################################################################################################### <----------------------------- Remover na versão final

        #button = tk.Button(self, text="Abrir Janela para testes", command=self.controladores)
        #button.grid(row=1, column=2)

        ###################################################################################################

        button = tk.Button(self, text="Telemetria", command=self.telemetria)
        button.grid(row=0, column=1)

        ###################################################################################################

        self.combobox = ttk.Combobox(self)
        self.combobox.grid(row=0, column=0, padx=10)

        botao_atualizar = tk.Button(self, text="Atualizar Portas", command=self.atualizar_portas)
        botao_atualizar.grid(row=1, column=0, padx=10)

        self.botao_conectar = tk.Button(self, text="Iniciar Conexão", command=self.alternar_conexao, bg="green", fg="white")
        self.botao_conectar.grid(row=0, column=2, padx=10)

        # Ligando o evento de seleção à função
        self.combobox.bind("<<ComboboxSelected>>", self.porta_selecionada) # <---------- pode remover a chamada depois, só printa pra falar q realmente selecionou

        # Chamando a função para preencher as portas ao iniciar o programa
        self.atualizar_portas()

        ###################################################################################################

        # Cria as labels para renderizar as imagens do painel nelas
        self.image_label_temperatura = tk.Label(self)
        self.image_label_temperatura.grid(row=2, column=0, padx=10, sticky='nsew')

        self.image_label_velocidade = tk.Label(self)
        self.image_label_velocidade.grid(row=2, column=1, padx=10, sticky='nsew')

        self.image_label_combustivel = tk.Label(self)
        self.image_label_combustivel.grid(row=2, column=2, padx=10, sticky='nsew')

        self.image_label_marcha = tk.Label(self)
        self.image_label_marcha.grid(row=3, column=0, padx=10, sticky='nsew')

        ###################################################################################################

        # Ajuste das colunas para expandir os gráficos
        self.grid_columnconfigure(0, weight=1)  # Temperatura
        self.grid_columnconfigure(1, weight=1)  # Temperatura
        self.grid_columnconfigure(2, weight=1)  # Velocidade

    ###################################################################################################

    @staticmethod
    def serial_ports():
        """ Lista as portas serias
                :raises EnvironmentError:
                    Se não for suportado pelo sistema
                :returns:
                    Uma lista com as portas serias disponiveis no sistema"""

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def atualizar_portas(self):
        portas = self.serial_ports()
        self.combobox['values'] = portas  # Define as portas na Combobox
        if portas:
            self.combobox.set("Selecione uma porta")
        else:
            self.combobox.set("Selecione uma porta")

    def porta_selecionada(self, event):
        print("Porta selecionada:", self.combobox.get()) # <-------------------------------- pode remover depois, só printa pra falar q realmente selecionou

    ###################################################################################################

    def create_graph(self):
        # Cria um frame para o gráfico
        self.graph_frame = tk.Frame(self)
        self.graph_frame.grid(row=3, column=1, padx=10, pady=10, sticky='nsew')

        # Configura o gráfico do Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.linha, = self.ax.plot(self.tempo, self.velocidade_data, '-')  # Linha sem pontos
        self.ax.set_xlim(0, 60)
        self.ax.set_ylim(0, 180)
        self.ax.set_title("Variação da Velocidade em Tempo Real")
        self.ax.set_xlabel("Tempo (segundos)")
        self.ax.set_ylabel("Velocidade")

        # Integra o gráfico ao Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Inicia a primeira atualização do gráfico
        #self.after_id = self.after(50, self.atualizar_grafico)  # Atualiza a cada 50 milissegundos

    ###################################################################################################

    def atualizar_grafico(self, velocidade=None):
        if self.thread_grafico:
            return  # Se uma thread já estiver em execução, não cria outra

        def atualizar():
            self.thread_grafico = True  # Bloqueia a execução de outras threads
            
            # Verifica se há uma nova velocidade para atualizar o gráfico
            if velocidade is not None:
                tempo_decorrido = time.time() - self.tempo_inicial
                nova_velocidade = float(velocidade)

                # Adicionar dados apenas se o tempo decorrido for maior que 100 ms para reduzir frequência
                if not self.tempo or (tempo_decorrido - self.tempo[-1]) > 0.1:
                    self.tempo.append(tempo_decorrido)
                    self.velocidade_data.append(nova_velocidade)
                    self.linha.set_xdata(self.tempo)
                    self.linha.set_ydata(self.velocidade_data)
                    self.canvas.draw()

                # Ajusta os limites dos eixos para acompanhar os dados
                max_tempo = max(self.tempo) if self.tempo else 60
                self.ax.set_xlim(0, max(60, max_tempo))
                self.ax.set_ylim(0, 180)

            # Continua atualização com intervalo maior, se o tempo não tiver passado de 60 segundos
            if time.time() - self.tempo_inicial < 60:
                self.after_id = self.after(500, self.atualizar_grafico)  # Intervalo de 100 ms
            else:
                self.reset_grafico()

            self.thread_grafico = False  # Libera para outra execução de thread

        # Inicia a thread para rodar a função em segundo plano
        thread = threading.Thread(target=atualizar)
        thread.daemon = True  # A thread será finalizada quando o programa terminar
        thread.start()

    def reset_grafico(self):
        # Cancela e redefine os dados
        self.after_cancel(self.after_id)
        self.tempo.clear()
        self.velocidade_data.clear()
        self.tempo_inicial = time.time()

    ###################################################################################################

    def controladores(self):
        slider_window = tk.Toplevel(self)
        slider_window.geometry("500x170")
        slider_window.title("Janela de teste da interface")
        slider_window.resizable(False, False)

        for i in range(8):  # Adapte o número de colunas conforme necessário
            slider_window.grid_columnconfigure(i, weight=1)

        ############################

        # Criar a barra deslizante para velocidade (horizontal)
        slider = ttk.Scale(slider_window, from_=0, to=160, orient='horizontal', command=self.update_velocidade)
        slider.set(self.velocidade)
        slider.grid(row=0, column=1, columnspan=2, pady=5, padx=5)

        label_vel = tk.Label(slider_window, text="Velocidade")
        label_vel.grid(row=1, column=1, columnspan=2, pady=5)

        ############################

        # Criar a barra deslizante para combustível (horizontal)
        slider_combustivel = ttk.Scale(slider_window, from_=0, to=3000, orient='horizontal', command=self.update_combustivel)
        slider_combustivel.set(self.combustivel)
        slider_combustivel.grid(row=0, column=3, columnspan=2, pady=5, padx=5)

        label_com = tk.Label(slider_window, text="Combustível")
        label_com.grid(row=1, column=3, columnspan=2, pady=5)

        ############################

        # Criar a barra deslizante para temperatura (vertical)
        slider_temperatura = ttk.Scale(slider_window, from_=200, to=0, orient='vertical', command=self.update_temperature)
        slider_temperatura.set(self.temperatura)
        slider_temperatura.grid(row=0, column=5, rowspan=2, pady=5, padx=5, sticky='ns')

        label_tem = tk.Label(slider_window, text="Temperatura")
        label_tem.grid(row=2, column=5, pady=5)

        ############################

        # Criar a barra deslizante para marcha (vertical)
        slider_marcha = ttk.Scale(slider_window, from_=5, to=-1, orient='vertical', command=self.update_marcha)
        slider_marcha.set(self.marcha)
        slider_marcha.grid(row=0, column=7, rowspan=2, pady=5, padx=5, sticky='ns')

        label_mar = tk.Label(slider_window, text="Marcha")
        label_mar.grid(row=2, column=7, pady=5)

        ############################

    ###################################################################################################

    def update_graph(self):
        # Criar os gráficos e obter as imagens no buffer chamando as funções específicas
        buffer_velocidade = plot_image_velocidade(self.velocidade)
        buffer_combustivel = plot_image_combustivel(self.combustivel)
        buffer_temperatura = plot_image_temperatura(self.temperatura)
        buffer_marcha = plot_image_marcha(self.marcha)

        # Atualizar as imagens exibidas
        self.display_image(buffer_velocidade, self.image_label_velocidade)
        self.display_image(buffer_combustivel, self.image_label_combustivel)
        self.display_image(buffer_temperatura, self.image_label_temperatura)
        self.display_image(buffer_marcha, self.image_label_marcha)

    ###################################################################################################

    def update_velocidade(self, value):
        # Atualiza o slider
        self.velocidade = int(float(value))

        # Atualizar o medidor de velocidade
        buffer_velocidade = plot_image_velocidade(self.velocidade)
        self.display_image(buffer_velocidade, self.image_label_velocidade)

        self.atualizar_valor_tabela("Velocidade", f"{self.velocidade} km/h")

    def update_temperature(self, value):
        # Atualiza o valor da temperatura
        self.temperatura = int(float(value))

        # Atualizar o gráfico relacionado à temperatura
        buffer_temperatura = plot_image_temperatura(self.temperatura)
        self.display_image(buffer_temperatura, self.image_label_temperatura)

        self.atualizar_valor_tabela("Temperatura", f"{self.temperatura} °C")

    def update_combustivel(self, value):
        # Atualiza o valor do combustível
        self.combustivel = int(float(value))

        # Atualizar o gráfico relacionado ao combustível
        buffer_combustivel = plot_image_combustivel(self.combustivel)
        self.display_image(buffer_combustivel, self.image_label_combustivel)

    def update_marcha(self, value):
        # Atualiza o valor da marcha
        self.marcha = int(float(value))

        # Atualizar o gráfico relacionado à marcha
        buffer_marcha = plot_image_marcha(self.marcha)
        self.display_image(buffer_marcha, self.image_label_marcha)

    def display_image(self, buffer, label, size=(466, 333)):
        # Atualiza o rótulo com a imagem
        img = Image.open(buffer)
        img = img.resize(size, Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk  # Mantenha uma referência da imagem

    ###################################################################################################
        
    def telemetria(self):
        # Configura a janela da tabela
        self.tabela_window = tk.Toplevel(self.master)
        self.tabela_window.title("Tabela de Valores")
        self.tabela_window.geometry("500x400")

        # Tabela (Treeview)
        self.tabela = ttk.Treeview(self.tabela_window, columns=("Variável", "Valor"), show="headings")
        self.tabela.heading("Variável", text="Variável")
        self.tabela.heading("Valor", text="Valor")
        self.tabela.pack(pady=20, fill="both", expand=True)

        linhas_iniciais = [
            ("Velocidade", f"{self.velocidade} Km/h"),
            ("Velocidade Média", f"{self.vmed} Km/h"),
            ("Distancia total", f"{self.distancia_total} metros"),
            ("Aceleração", f"{self.aceleracao} m/s²"),
            ("Consumo", f"{self.consumo} Km/L"),
            ("Temperatura", f"{self.temperatura} °C"),
            ("Temperatura Média", f"{self.tmed} °C")
        ]

        for variavel, valor in linhas_iniciais:
            item_id = self.tabela.insert('', 'end', values=(variavel, valor))
            self.itens_tabela[variavel] = item_id

            #print(f"id da variavel: " + variavel + " | " + self.itens_tabela[variavel]) # Mostra o id de cada linha
        
    def atualizar_valor_tabela(self, variavel, novo_valor): 
        # Verifica se o nome existe no dicionário de IDs
        if variavel in self.itens_tabela:
            item_id = self.itens_tabela[variavel]
            
            # Tenta atualizar na tabela se ela estiver aberta
            if hasattr(self, 'tabela') and self.tabela:
                try:
                    self.tabela.item(item_id, values=(variavel, novo_valor))
                    #print(f"Valor atualizado para {variavel}: {novo_valor}")
                except TclError:
                    #print("Erro: A tabela está fechada ou inacessível.")
                    return

            # As linhas de baixo estão comentadas pois gastam ciclos de processamento, remova o '#' somente para realizar testes!
            """
            else:
                print(f"A tabela está fechada; atualização de '{variavel}' não realizada.")
        else:
            print(f"Item '{variavel}' não encontrado na tabela.")"""

    ###################################################################################################

    def fechar_janela(self):
        self.desconectar()
        # Cancela qualquer atualização pendente no gráfico
        if self.after_id is not None:
            self.after_cancel(self.after_id)  # Cancela o loop do after
        self.quit()  # Encerra o loop do Tkinter
        self.destroy()  # Destrói a janela do Tkinter

# Executar a aplicação
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()