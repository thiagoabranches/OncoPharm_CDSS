import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Configurações Visuais Profissionais
plt.style.use('bmh')
plt.rcParams.update({'font.size': 12, 'figure.autolayout': True})

INPUT_FILE = "data/processed/dados_limpos.csv"
OUTPUT_IMG = "simulacao_pk.png"

def simulate_pk_one_compartment(dose_mg, clearance_L_h=3.0, vd_L=20.0, hours=24):
    k = clearance_L_h / vd_L
    t = np.linspace(0, hours, 200)
    conc = (dose_mg / vd_L) * np.exp(-k * t)
    return t, conc

def run_simulation():
    # CORRECAO: Removido emoji do print
    print("[INFO] Gerando Grafico PK em Alta Definicao (300 DPI)...")
    
    if not os.path.exists(INPUT_FILE):
        dose_val = 75.0
        pid = "Simulado"
    else:
        try:
            df = pd.read_csv(INPUT_FILE)
            dose_str = df.iloc[0]['dose_cisplatina']
            dose_val = float(dose_str.replace('mg', '').strip())
            pid = df.iloc[0]['id_paciente']
        except:
            dose_val = 75.0
            pid = "Simulado"

    t, cp = simulate_pk_one_compartment(dose_val)

    # Plotagem HD
    plt.figure(figsize=(10, 6), dpi=300)
    plt.plot(t, cp, label=f'Cisplatina {dose_val}mg (IV)', color='#2E86C1', linewidth=3)
    plt.fill_between(t, cp, alpha=0.1, color='#2E86C1')
    plt.axhline(y=1.5, color='#E74C3C', linestyle='--', linewidth=2, label='Limiar Toxico')
    
    plt.title(f'Perfil Farmacocinetico: Paciente {pid}', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Tempo apos infusao (horas)', fontsize=12)
    plt.ylabel('Concentracao Plasmatica (mg/L)', fontsize=12)
    plt.legend(frameon=True, facecolor='white', framealpha=1, fontsize=10)
    plt.grid(True, which='major', linestyle='--', alpha=0.7)
    plt.minorticks_on()
    
    plt.savefig(OUTPUT_IMG, dpi=300, bbox_inches='tight')
    print(f"[OK] Grafico PK salvo: {OUTPUT_IMG}")

if __name__ == "__main__":
    run_simulation()
