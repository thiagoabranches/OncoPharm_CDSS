import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Configurações
INPUT_FILE = "data/processed/dados_limpos.csv"
OUTPUT_IMG = "simulacao_pk.png"

def simulate_pk_one_compartment(dose_mg, clearance_L_h=3.0, vd_L=20.0, hours=24):
    """
    Simula modelo de um compartimento (IV Bolus).
    Fórmula: C(t) = (Dose / Vd) * exp(-k * t)
    """
    k = clearance_L_h / vd_L  # Constante de eliminação
    t = np.linspace(0, hours, 100)
    conc = (dose_mg / vd_L) * np.exp(-k * t)
    return t, conc

def run_simulation():
    print("🔬 Iniciando Simulação Farmacocinética (PK)...")
    
    if not os.path.exists(INPUT_FILE):
        print("❌ Erro: Execute o script de ETL primeiro.")
        return
        
    df = pd.read_csv(INPUT_FILE)
    
    # Extrair dose (ex: "75mg" -> 75.0)
    dose_str = df.iloc[0]['dose_cisplatina']
    dose_val = float(dose_str.replace('mg', '').strip())
    
    print(f"💊 Paciente ID {df.iloc[0]['id_paciente']} | Dose: {dose_val} mg")

    # Simulação
    t, cp = simulate_pk_one_compartment(dose_val)

    # Plotagem
    plt.figure(figsize=(10, 6))
    plt.plot(t, cp, label=f'Cisplatina {dose_val}mg', color='blue', linewidth=2)
    plt.axhline(y=1.5, color='red', linestyle='--', label='Limiar Tóxico')
    
    plt.title(f'Decaimento Plasmático Simulado (0-24h)')
    plt.xlabel('Tempo (h)')
    plt.ylabel('Concentração (mg/L)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(OUTPUT_IMG)
    print(f"📈 Gráfico salvo em: {os.path.abspath(OUTPUT_IMG)}")

if __name__ == "__main__":
    run_simulation()
