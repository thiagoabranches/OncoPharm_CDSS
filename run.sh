#!/bin/bash

# --- 1. INSTALAÇÃO DE DEPENDÊNCIAS DO SISTEMA (Linux Packages) ---
# Usamos apt-get para instalar o essencial que o Python precisa
sudo apt-get update && sudo apt-get install -y python3-pandas python3-numpy python3-scikit-learn

# --- 2. GERAÇÃO DE DADOS E INICIALIZAÇÃO ---
# Cria a pasta de dados e executa o gerador de dados antes do app
mkdir -p src/data/processed
python src/data/generate_synthetic.py

# Inicia o aplicativo Streamlit
python -m streamlit run src/app/dashboard.py
