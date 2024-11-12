import subprocess
import sys
import threading

def instalar_pip():
    try:
        # Verifica se o pip já está instalado
        import pip
    except ImportError:
        # Baixa e instala o pip
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])
        print("pip foi instalado com sucesso!")

def instalar_pacote(pacote):
    try:
        # Comando para instalar o pacote usando o pip
        comando = [sys.executable, "-m", "pip", "install", pacote]
        # Executa o comando usando subprocess
        subprocess.check_call(comando)
        print(f"O pacote '{pacote}' foi instalado com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro ao instalar '{pacote}': {e}")

# Instala o pip (caso não esteja instalado)
instalar_pip()

# Lista de pacotes a serem instalados
pacotes = ["imagetk", "plotly", "pillow", "matplotlib", "kaleido", "pyserial", "digi-xbee"]

# Cria uma lista de threads para instalar cada pacote simultaneamente
threads = [threading.Thread(target=instalar_pacote, args=(pacote,)) for pacote in pacotes]

# Inicia todas as threads
for thread in threads:
    thread.start()

# Aguarda todas as threads terminarem
for thread in threads:
    thread.join()
