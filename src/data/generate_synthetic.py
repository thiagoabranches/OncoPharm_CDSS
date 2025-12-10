import pandas as pd
import numpy as np
import os

DATA_DIR = "data/processed"
os.makedirs(DATA_DIR, exist_ok=True)

# --- 1. DATASET DE TREINAMENTO (Para a IA aprender Gravidade) ---
dados_treino = [
    {"texto": "Paciente com leve rash cutaneo, sem dor.", "gravidade": "Grau 1 (Leve)"},
    {"texto": "Fadiga leve ao final do dia, mantendo atividades.", "gravidade": "Grau 1 (Leve)"},
    {"texto": "Neutropenia febril grave, necessita internacao.", "gravidade": "Grau 3/4 (Grave)"},
    {"texto": "Nefrotoxicidade aguda, creatinina triplicou, anuria.", "gravidade": "Grau 3/4 (Grave)"},
    {"texto": "Paciente assintomatico.", "gravidade": "Grau 0 (Normal)"}
]
df_treino = pd.DataFrame(dados_treino * 5) 
df_treino.to_csv(os.path.join(DATA_DIR, "treino_ia.csv"), index=False)

# --- 2. PACIENTES DO DASHBOARD (Aumentando a lista para 5) ---
pacientes = [
    {"id": 1001, "nome": "Maria Silva", "idade": 45, "sexo": "F", "peso": 60.0, "bsa": 1.65, "status": "Tratamento"},
    {"id": 1002, "nome": "João Santos", "idade": 68, "sexo": "M", "peso": 75.0, "bsa": 1.88, "status": "Risco Elevado"},
    {"id": 1003, "nome": "Ana Costa", "idade": 52, "sexo": "F", "peso": 68.0, "bsa": 1.70, "status": "Monitoramento"},
    {"id": 1004, "nome": "Carlos Pereira", "idade": 71, "sexo": "M", "peso": 82.0, "bsa": 1.95, "status": "Alerta PK"},
    {"id": 1005, "nome": "Sofia Mendes", "idade": 38, "sexo": "F", "peso": 55.0, "bsa": 1.58, "status": "Estável"}
]
df_pacientes = pd.DataFrame(pacientes)

# --- 3. EXAMES ---
exames = [
    {"patient_id": 1001, "tipo": "Creatinina", "valor": 0.8},
    {"patient_id": 1002, "tipo": "Creatinina", "valor": 1.9},
    {"patient_id": 1003, "tipo": "Creatinina", "valor": 0.9},
    {"patient_id": 1004, "tipo": "Creatinina", "valor": 1.5},
    {"patient_id": 1005, "tipo": "Creatinina", "valor": 0.7},
]
df_exames = pd.DataFrame(exames)

# --- 4. NOTAS CLÍNICAS ---
notas = [
    {"patient_id": 1001, "texto": "Paciente refere fadiga leve, mantendo atividades."},
    {"patient_id": 1002, "texto": "Apresenta sinais de nefrotoxicidade aguda e oliguria severa."},
    {"patient_id": 1003, "texto": "Relata rash cutaneo difuso e leve prurido."},
    {"patient_id": 1004, "texto": "Sem queixas ativas. Exames de rotina demonstram alteração renal recente."},
    {"patient_id": 1005, "texto": "Evolução sem intercorrências; tratamento bem tolerado."}
]
df_notas = pd.DataFrame(notas)

# Salvar
df_pacientes.to_csv(os.path.join(DATA_DIR, "pacientes_mock.csv"), index=False)
df_exames.to_csv(os.path.join(DATA_DIR, "exames_mock.csv"), index=False)
df_notas.to_csv(os.path.join(DATA_DIR, "notas_mock.csv"), index=False)
print("[OK] Dados Mock gerados com 5 pacientes.")
