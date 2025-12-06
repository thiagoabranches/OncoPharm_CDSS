import pandas as pd
import os

# Caminhos (Paths)
RAW_PATH = "data/raw/dados_teste.csv"
PROCESSED_PATH = "data/processed/dados_limpos.csv"

def run_etl():
    print("🚀 Iniciando Pipeline de ETL...")
    
    # 1. Verificação de Segurança
    if not os.path.exists(RAW_PATH):
        print(f"❌ Erro: Arquivo não encontrado em {RAW_PATH}")
        return

    # 2. Extração (Extract)
    try:
        df = pd.read_csv(RAW_PATH)
        print(f"✅ Dados Carregados: {len(df)} registros encontrados.")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return

    # 3. Transformação (Transform)
    # Padronização simples para demonstrar o fluxo
    print("🔄 Normalizando dados...")
    df.columns = [col.lower().strip() for col in df.columns] # Padroniza colunas
    
    # Exemplo de regra de negócio: Filtrar apenas toxicidades
    # (Num cenário real, aqui entraria a limpeza com 'ehrapy')
    
    # 4. Carga (Load)
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"💾 Dados processados salvos em: {PROCESSED_PATH}")
    print("---------------------------------------")
    print("Amostra dos dados processados:")
    print(df.head())

if __name__ == "__main__":
    run_etl()
