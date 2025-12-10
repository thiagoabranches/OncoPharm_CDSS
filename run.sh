#!/bin/bash
set -e

# --- 1. INSTALAÇÃO DE DEPENDÊNCIAS DO SISTEMA (Linux Packages) ---
# O comando apt-get é crucial e precisa ser rodado antes de tudo
sudo apt-get update && sudo apt-get install -y python3-pandas python3-numpy python3-scikit-learn

# --- 2. GERAÇÃO DE DADOS (CRIA OS ARQUIVOS) ---
# Navega para a raiz do projeto e chama o script de dados diretamente.
# Usamos 'python3' para maior compatibilidade no ambiente Streamlit.
mkdir -p src/data/processed
python3 src/data/generate_synthetic.py

# --- 3. INICIA O APLICATIVO ---
# Inicia o Streamlit
python3 -m streamlit run src/app/dashboard.py
