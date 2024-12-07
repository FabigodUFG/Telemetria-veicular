import tkinter as tk
from tkinter import ttk

class TabelaTelemetria:
    def __init__(self, master):
        self.master = master
        self.tabela = None
        self.itens_tabela = {}

    def criar_tabela(self, velocidade, vmed, distancia_total, aceleracao, consumo, temperatura, tmed):
        # Configura a janela da tabela
        tabela_window = tk.Toplevel(self.master)
        tabela_window.title("Tabela da telemetria")
        tabela_window.geometry("500x400")

        # Tabela (Treeview)
        self.tabela = ttk.Treeview(tabela_window, columns=("Variável", "Valor"), show="headings")
        self.tabela.heading("Variável", text="Variável")
        self.tabela.heading("Valor", text="Valor")
        self.tabela.pack(pady=20, fill="both", expand=True)

        linhas_iniciais = [
            ("Velocidade", f"{velocidade} Km/h"),
            ("Velocidade Média", f"{vmed} Km/h"),
            ("Distancia total", f"{distancia_total} metros"),
            ("Aceleração", f"{aceleracao} m/s²"),
            ("Consumo", f"{consumo} Km/L"),
            ("Temperatura", f"{temperatura} °C"),
            ("Temperatura Média", f"{tmed} °C")
        ]

        # Preenche a tabela e guarda os IDs dos itens
        for variavel, valor in linhas_iniciais:
            item_id = self.tabela.insert('', 'end', values=(variavel, valor))
            self.itens_tabela[variavel] = item_id

    def atualizar_valor(self, variavel, novo_valor): 
        # Verifica se o nome existe no dicionário de IDs
        if variavel in self.itens_tabela:
            item_id = self.itens_tabela[variavel]
            
            # Verifica se a tabela está inicializada e ativa
            if self.tabela:
                try:
                    self.tabela.item(item_id, values=(variavel, novo_valor))
                except tk.TclError:
                    print("Erro: A tabela não está acessível.")
        else:
            print(f"Item '{variavel}' não encontrado na tabela.")
