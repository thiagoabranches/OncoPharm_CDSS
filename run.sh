#!/bin/bash
set -e

# --- 1. INSTALAÇÃO DE DEPENDÊNCIAS DO SISTEMA (Linux Packages) ---
# Força atualização e instalação para garantir as bibliotecas do sistema
sudo apt-get update && sudo apt-get install -y python3-pandas python3-numpy python3-scikit-learn

# --- 2. GERAÇÃO DE DADOS (CRIA OS ARQUIVOS) ---
# Cria a pasta e garante que o Python crie os dados.
mkdir -p src/data/processed
python3 src/data/generate_synthetic.py

# --- 3. INICIA O APLICATIVO ---
# Inicia o Streamlit
python3 -m streamlit run src/app/dashboard.py
