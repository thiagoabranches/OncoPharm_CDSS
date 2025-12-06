import sqlite3
import pandas as pd
import os

# Caminhos
DB_PATH = "database/oncopharm.db"
SCHEMA_PATH = "database/schemas/01_omop_oncology_episode.sql"
CSV_PATH = "data/processed/dados_limpos.csv"

def init_database():
    print("🗄️  Inicializando Banco de Dados OMOP (SQLite)...")
    
    # 1. Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    
    # 2. Ler e executar o esquema SQL (CORREÇÃO: encoding='utf-8')
    # Isso garante que o Python entenda o arquivo criado pelo Git Bash
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)
        
    print("✅ Tabelas OMOP criadas com sucesso.")
    return conn

def load_data(conn):
    print("📥 Carregando dados do CSV para SQL...")
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Erro: Arquivo {CSV_PATH} não encontrado. Rode o ETL 01.")
        return

    df = pd.read_csv(CSV_PATH)
    cursor = conn.cursor()
    
    for index, row in df.iterrows():
        # Dados do episódio
        episode_data = (
            row['id_paciente'],      # episode_id
            row['id_paciente'],      # person_id
            32531,                   # episode_concept_id
            '2025-12-06',            # episode_start_date
            1,                       # episode_number
            f"Dose: {row['dose_cisplatina']} | Tox: {row['toxicidade_renal']}" # source_value
        )
        
        # Query de Inserção segura
        sql = """
        INSERT INTO episode (
            episode_id, person_id, episode_concept_id, 
            episode_start_date, episode_number, episode_source_value,
            episode_object_concept_id, episode_type_concept_id
        ) VALUES (?, ?, ?, ?, ?, ?, 0, 0);
        """
        try:
            cursor.execute(sql, episode_data)
        except sqlite3.IntegrityError:
            print(f"⚠️ Aviso: Registro {row['id_paciente']} já existe.")
        
    conn.commit()
    print(f"💾 {len(df)} registros processados na tabela 'episode'.")

def verify_data(conn):
    print("\n🔎 Verificando dados via SQL:")
    try:
        df_sql = pd.read_sql_query("SELECT * FROM episode", conn)
        print(df_sql[['person_id', 'episode_source_value']].head())
    except Exception as e:
        print(f"Erro ao ler SQL: {e}")

if __name__ == "__main__":
    # Remove banco antigo para garantir teste limpo
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            print("⚠️ O banco de dados está aberto em outro programa. Feche o Streamlit e tente de novo.")
        
    conn = init_database()
    load_data(conn)
    verify_data(conn)
    conn.close()
