import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime
from PIL import Image

# --- Configuração da Página ---
st.set_page_config(page_title="OncoPharm CDSS", layout="wide", page_icon="🏥")

st.title("🏥 OncoPharm: Plataforma de Oncologia de Precisão")
st.markdown("### 🔌 Conexão: Banco de Dados OMOP (SQLite)")
st.markdown("---")

# --- Funções de Backend ---
DB_PATH = "database/oncopharm.db"
LOG_PATH = "data/processed/decisoes_clinicas.txt"

def get_data_from_sql():
    """Conecta ao banco e retorna o histórico."""
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        person_id as 'ID Paciente',
        episode_start_date as 'Data Início',
        episode_number as 'Ciclo',
        episode_source_value as 'Detalhes (Dose/Tox)'
    FROM episode
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def save_decision_log(paciente_id, acao, notas):
    """Registra a decisão do farmacêutico (Auditoria)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] PACIENTE: {paciente_id} | AÇÃO: {acao} | NOTAS: {notas}\n"
    
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

# --- Interface do Usuário ---

# 1. Carregar Dados do SQL
df_sql = get_data_from_sql()
paciente_selecionado = None

col_db, col_sim = st.columns([1, 2])

with col_db:
    st.subheader("🗄️ Prontuário Eletrônico")
    if df_sql is not None and not df_sql.empty:
        st.success("Conexão SQL Ativa ✅")
        st.dataframe(df_sql, use_container_width=True, hide_index=True)
        
        # Seleção automática do primeiro paciente para o protótipo
        paciente_selecionado = df_sql.iloc[0]['ID Paciente']
        detalhes = df_sql.iloc[0]['Detalhes (Dose/Tox)']
        st.info(f"Paciente em Foco: {paciente_selecionado}")
    else:
        st.error("Erro: Banco de dados vazio. Execute o ETL 02.")
        st.stop()

# 2. Motor Analítico (IA e PK)
with col_sim:
    st.subheader("🧠 Inteligência Clínica")
    tab1, tab2 = st.tabs(["📉 Farmacocinética (PK)", "🔮 Risco de Toxicidade (IA)"])
    
    with tab1:
        if os.path.exists("simulacao_pk.png"):
            st.image(Image.open("simulacao_pk.png"), caption="Decaimento Plasmático (1 Compartimento)")
        else:
            st.warning("Execute a simulação PK.")
            
    with tab2:
        if os.path.exists("curva_sobrevivencia_toxicidade.png"):
            st.image(Image.open("curva_sobrevivencia_toxicidade.png"))
            st.error(f"⚠️ ALERTA: Genótipo de Risco Detectado.\nRecomendação do Modelo: Avaliar redução preventiva.")
        else:
            st.warning("Execute o modelo de IA.")

# 3. INTERFACE DE DECISÃO (Human-in-the-Loop) - Restaurada e Melhorada!
st.markdown("---")
st.subheader("📝 Farmácia Clínica: Tomada de Decisão & Registro")

# Criamos um container visualmente distinto para a ação do farmacêutico
with st.container():
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c1:
        st.markdown("**1. Ajuste de Dose**")
        decisao_dose = st.radio(
            "Selecione a intervenção:",
            ("Manter Dose Prescrita", 
             "Reduzir 20% (Preventivo)", 
             "Reduzir 50% (Toxicidade Grave)", 
             "Suspender Ciclo"),
            index=1 # Sugere redução por padrão devido ao alerta da IA
        )
    
    with c2:
        st.markdown("**2. Acompanhamento Clínico**")
        notas_clinicas = st.text_area(
            "Justificativa e Notas de Evolução:",
            value="Paciente apresenta variante genética de risco. IA sugere alta probabilidade de evento adverso em 30 dias. Sugiro redução preventiva conforme protocolo institucional.",
            height=130
        )
        
    with c3:
        st.markdown("**3. Registro**")
        st.write("") # Espaçamento
        st.write("")
        if st.button("💾 REGISTRAR DECISÃO", type="primary", use_container_width=True):
            if paciente_selecionado:
                save_decision_log(paciente_selecionado, decisao_dose, notas_clinicas)
                st.success("✅ Intervenção registrada no prontuário!")
                st.balloons()
            else:
                st.error("Nenhum paciente selecionado.")

st.markdown("---")
st.caption("OncoPharm CDSS v1.2 | Governança: DVC + SQL | Log de Auditoria Ativo")
