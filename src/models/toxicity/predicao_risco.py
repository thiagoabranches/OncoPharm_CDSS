import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Tenta importar scikit-survival, se falhar, avisa
try:
    from sksurv.linear_model import CoxPHSurvivalAnalysis
    from sksurv.util import Surv
except ImportError:
    print("[ERRO] scikit-survival nao instalado. Rode: pip install scikit-survival")
    exit()

import os

# Configurações Visuais Profissionais
plt.style.use('bmh')
plt.rcParams.update({'font.size': 12})

OUTPUT_IMG = "curva_sobrevivencia_toxicidade.png"

def generate_synthetic_cohort(n=200):
    np.random.seed(42)
    data = pd.DataFrame({
        'dose_mg': np.random.normal(70, 15, n),
        'variante_genetica': np.random.binomial(1, 0.3, n),
        'idade': np.random.normal(60, 10, n)
    })
    risco_base = np.exp(0.05 * data['dose_mg'] + 1.5 * data['variante_genetica'])
    tempo_ate_evento = np.random.exponential(1000 / risco_base)
    data['teve_toxicidade'] = tempo_ate_evento < 30 
    data['dias_observacao'] = tempo_ate_evento
    return data

def run_toxicity_model():
    # CORRECAO: Removido emoji
    print("[INFO] Gerando Grafico de Risco em Alta Definicao (300 DPI)...")
    
    train_data = generate_synthetic_cohort()
    X = train_data[['dose_mg', 'variante_genetica', 'idade']]
    y = Surv.from_dataframe('teve_toxicidade', 'dias_observacao', train_data)
    
    estimator = CoxPHSurvivalAnalysis()
    estimator.fit(X, y)

    paciente_teste = pd.DataFrame({
        'dose_mg': [75.0],
        'variante_genetica': [1], 
        'idade': [65]
    })
    
    pred_surv = estimator.predict_survival_function(paciente_teste)
    
    plt.figure(figsize=(10, 6), dpi=300)
    
    for fn in pred_surv:
        plt.step(fn.x, fn.y, where="post", color='#8E44AD', linewidth=3, label='Prob. Livre de Toxicidade')
        plt.fill_between(fn.x, fn.y, step="post", alpha=0.1, color='#8E44AD')
        
    plt.title(f'Previsao de Sobrevida Livre de Eventos (30 dias)', fontsize=14, fontweight='bold', pad=20)
    plt.ylabel('Probabilidade (%)', fontsize=12)
    plt.xlabel('Dias do Ciclo', fontsize=12)
    plt.ylim(0, 1.05)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='lower left', frameon=True, facecolor='white')
    
    plt.savefig(OUTPUT_IMG, dpi=300, bbox_inches='tight')
    print(f"[OK] Grafico de Risco salvo: {OUTPUT_IMG}")

if __name__ == "__main__":
    run_toxicity_model()
