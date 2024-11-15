#!/bin/bash

# Atualiza o pip para a versão mais recente
python3 -m pip install --upgrade pip

# Instala a partir do requirements.txt (se existir)
if [ -f "dependencies.txt" ]; 
    then
    echo "Instalando a partir da lista de dependências..."
    pip install -r dependencies.txt
else
    echo "Arquivo dependencies.txt não encontrado, instalando internamente..."
    # Adicione suas dependências aqui
    pip install imagetk
    pip install plotly
    pip install pillow
    pip install kaleido
    pip install matplotlib
fi

clear && echo "Instalação de dependências concluída."
