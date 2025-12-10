#!/bin/bash
set -e

# --- 1. INSTALAÇÃO DE DEPENDÊNCIAS DO SISTEMA (Linux Packages) ---
sudo apt-get update && sudo apt-get install -y python3-pandas python3-numpy python3-scikit-learn

# --- 2. INSTALAÇÃO DE DEPENDÊNCIAS PYTHON (Incluindo Groq e Transformers) ---
pip install -r requirements.txt

# --- 3. GERAÇÃO DE DADOS (CRIA OS ARQUIVOS MOCK) ---
mkdir -p src/data/processed
# A versão mais completa do generate_synthetic.py (com 5 pacientes) é executada
python3 src/data/generate_synthetic.py

# --- 4. INICIA O APLICATIVO ---
python3 -m streamlit run src/app/dashboard.py
