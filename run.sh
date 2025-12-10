#!/bin/bash
# 1. Cria a pasta de dados se não existir
mkdir -p src/data/processed
# 2. Roda o script para gerar os mocks de pacientes e treino da IA
python src/data/generate_synthetic.py
# 3. Inicia o aplicativo Streamlit
python -m streamlit run src/app/dashboard.py
