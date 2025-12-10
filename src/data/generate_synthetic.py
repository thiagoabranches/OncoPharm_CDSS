import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configuração
DATA_DIR = "data/processed"
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Pacientes (Cenários variados para o Artigo)
pacientes = [
    {"id": 1001, "nome": "Maria Silva (Normal)", "idade": 45, "sexo": "F", "peso": 60.0, "altura": 165, "bsa": 1.65},
    {"id": 1002, "nome": "João Santos (Risco Renal)", "idade": 68, "sexo": "M", "peso": 75.0, "altura": 172, "bsa": 1.88},
    {"id": 1003, "nome": "Ana Costa (Toxicidade NLP)", "idade": 52, "sexo": "F", "peso": 68.0, "altura": 160, "bsa": 1.70},
    {"id": 1004, "nome": "Carlos Pereira (Crítico)", "idade": 74, "sexo": "M", "peso": 55.0, "altura": 168, "bsa": 1.62},
    {"id": 1005, "nome": "Fernanda Lima (Jovem)", "idade": 32, "sexo": "F", "peso": 58.0, "altura": 170, "bsa": 1.67}
]
df_pacientes = pd.DataFrame(pacientes)

# 2. Exames (Simulando HL7)
exames = [
    {"patient_id": 1001, "data": "2023-12-08", "tipo": "Creatinina", "valor": 0.8, "unidade": "mg/dL"},
    {"patient_id": 1001, "data": "2023-12-08", "tipo": "Albumina", "valor": 4.0, "unidade": "g/dL"},
    {"patient_id": 1002, "data": "2023-12-08", "tipo": "Creatinina", "valor": 1.9, "unidade": "mg/dL"}, # Alto Risco
    {"patient_id": 1002, "data": "2023-12-08", "tipo": "Albumina", "valor": 3.2, "unidade": "g/dL"},
    {"patient_id": 1003, "data": "2023-12-08", "tipo": "Creatinina", "valor": 0.9, "unidade": "mg/dL"},
    {"patient_id": 1004, "data": "2023-12-08", "tipo": "Creatinina", "valor": 3.5, "unidade": "mg/dL"}, # Falência
    {"patient_id": 1005, "data": "2023-12-08", "tipo": "Creatinina", "valor": 0.7, "unidade": "mg/dL"},
]
df_exames = pd.DataFrame(exames)

# 3. Notas Clínicas (Simulando Texto Livre para NLP)
notas = [
    {"patient_id": 1001, "data": "2023-12-08", "texto": "Paciente assintomática. Boa tolerância."},
    {"patient_id": 1002, "data": "2023-12-08", "texto": "Fadiga leve. Diurese escurecida."},
    {"patient_id": 1003, "data": "2023-12-08", "texto": "Relata zumbido (tinnitus) e rash cutâneo nos braços."}, # Alerta NLP
    {"patient_id": 1004, "data": "2023-12-08", "texto": "Neutropenia febril e sinais de nefrotoxicidade aguda."}, # Crítico
    {"patient_id": 1005, "data": "2023-12-08", "texto": "Sem queixas."}
]
df_notas = pd.DataFrame(notas)

# Salvar
df_pacientes.to_csv(os.path.join(DATA_DIR, "pacientes_mock.csv"), index=False)
df_exames.to_csv(os.path.join(DATA_DIR, "exames_mock.csv"), index=False)
df_notas.to_csv(os.path.join(DATA_DIR, "notas_mock.csv"), index=False)
print("Dados gerados com sucesso!")
