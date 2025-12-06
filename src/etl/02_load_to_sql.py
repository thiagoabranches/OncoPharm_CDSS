import sqlite3
import pandas as pd
import os

# Caminhos
DB_PATH = "database/oncopharm.db"
SCHEMA_PATH = "database/schemas/01_omop_oncology_episode.sql"
CSV_PATH = "data/processed/dados_limpos.csv"

def init_database():
    print("[INFO] Inicializando Banco de Dados OMOP (SQLite)...")
    
    # 1. Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    
    # 2. Ler e executar o esquema SQL
    # encoding='utf-8' e essencial para ler o arquivo SQL corretamente
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            conn.executescript(schema_sql)
        print("[OK] Tabelas criadas.")
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de esquema nao encontrado: {SCHEMA_PATH}")
        return None
        
    return conn

def load_data(conn):
    if conn is None: return

    print("[INFO] Carregando dados do CSV para SQL...")
    
    if not os.path.exists(CSV_PATH):
        print(f"[ERRO] Arquivo {CSV_PATH} nao encontrado. Rode o ETL 01.")
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
            pass # Ignora duplicatas na carga inicial
        
    conn.commit()
    print(f"[OK] {len(df)} registros processados.")

def verify_data(conn):
    if conn is None: return
    print("\n[INFO] Verificando dados via SQL:")
    try:
        df_sql = pd.read_sql_query("SELECT * FROM episode LIMIT 5", conn)
        print(df_sql[['person_id', 'episode_source_value']])
    except Exception as e:
        print(f"Erro ao ler SQL: {e}")

if __name__ == "__main__":
    # Garante banco limpo
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except:
            pass
        
    conn = init_database()
    load_data(conn)
    verify_data(conn)
    if conn: conn.close()
