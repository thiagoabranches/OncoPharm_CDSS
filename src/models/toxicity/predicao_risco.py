import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.util import Surv

# Configurações
OUTPUT_IMG = "curva_sobrevivencia_toxicidade.png"

def generate_synthetic_cohort(n=200):
    """
    Gera dados fictícios para treinar o modelo.
    Fatores de risco simulados:
    - Variante Genética (0=Não, 1=Sim): Aumenta risco.
    - Dose (mg): Dose maior aumenta risco.
    """
    np.random.seed(42)
    
    # Criar DataFrame
    data = pd.DataFrame({
        'dose_mg': np.random.normal(70, 15, n), # Doses variando em torno de 70mg
        'variante_genetica': np.random.binomial(1, 0.3, n), # 30% tem a variante
        'idade': np.random.normal(60, 10, n)
    })
    
    # Simular o "tempo até a toxicidade" (Outcome)
    # A fórmula abaixo faz com que dose alta e genética diminuam o tempo livre de toxicidade
    risco_base = np.exp(0.05 * data['dose_mg'] + 1.5 * data['variante_genetica'])
    tempo_ate_evento = np.random.exponential(1000 / risco_base)
    
    # Definir status (True = Teve toxicidade, False = Livre de toxicidade/Censurado)
    data['teve_toxicidade'] = tempo_ate_evento < 30 # Toxicidade nos primeiros 30 dias
    data['dias_observacao'] = tempo_ate_evento
    
    return data

def run_toxicity_model():
    print("🤖 Iniciando Treinamento do Modelo de Sobrevivência (CoxPH)...")
    
    # 1. Obter dados de treino
    train_data = generate_synthetic_cohort()
    print(f"📊 Coorte de Treinamento: {len(train_data)} pacientes simulados.")
    
    # 2. Preparar dados para o scikit-survival (Matriz X e Vetor y estruturado)
    X = train_data[['dose_mg', 'variante_genetica', 'idade']]
    y = Surv.from_dataframe('teve_toxicidade', 'dias_observacao', train_data)
    
    # 3. Treinar o modelo
    estimator = CoxPHSurvivalAnalysis()
    estimator.fit(X, y)
    print("✅ Modelo treinado com sucesso!")
    
    # Mostrar os coeficientes (O que aumenta o risco?)
    print("\nFatores de Risco Aprendidos (Hazard Ratios - Log):")
    for feature, coef in zip(X.columns, estimator.coef_):
        print(f" - {feature}: {coef:.4f} (Valores positivos indicam maior risco)")

    # 4. Predição para o NOSSO paciente (Do arquivo CSV processado)
    # Vamos assumir dados complementares para ele (Idade 65, Com variante genética)
    paciente_teste = pd.DataFrame({
        'dose_mg': [75.0],        # Dose que extraímos antes
        'variante_genetica': [1], # Assumindo que ele tem a variante (pior cenário)
        'idade': [65]
    })
    
    print("\n🔮 Realizando predição para o Paciente Atual...")
    risk_score = estimator.predict(paciente_teste)[0]
    print(f"⚠️ Score de Risco Calculado: {risk_score:.2f}")

    # 5. Gerar Curva de Sobrevivência Livre de Toxicidade
    pred_surv = estimator.predict_survival_function(paciente_teste)
    
    plt.figure(figsize=(10, 6))
    for i, fn in enumerate(pred_surv):
        plt.step(fn.x, fn.y, where="post", color='purple', linewidth=2)
        
    plt.title(f'Probabilidade de Permanecer Livre de Toxicidade (30 dias)')
    plt.ylabel('Probabilidade Livre de Evento')
    plt.xlabel('Dias do Ciclo')
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3)
    
    plt.savefig(OUTPUT_IMG)
    print(f"📈 Curva de risco salva em: {OUTPUT_IMG}")

if __name__ == "__main__":
    run_toxicity_model()
