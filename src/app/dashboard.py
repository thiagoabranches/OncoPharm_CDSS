import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime
from PIL import Image
import sys

# --- Configuração Inicial ---
sys.path.append(os.path.abspath("src"))
try:
    from models.nlp.ae_detector import PharmacovigilanceNLP
    from integration.rpa.notivisa_bot import NotivisaAutomator
except ImportError:
    st.error("Erro critico: Modulos nao encontrados. Verifique a pasta src.")
    st.stop()

st.set_page_config(page_title="OncoPharm CDSS", layout="wide", page_icon="🏥")

# Inicialização de Sessão
if 'nlp_engine' not in st.session_state:
    st.session_state['nlp_engine'] = PharmacovigilanceNLP()
if 'notivisa_bot' not in st.session_state:
    st.session_state['notivisa_bot'] = NotivisaAutomator()
if 'notivisa_report' not in st.session_state:
    st.session_state['notivisa_report'] = ""

# Caminhos
DB_PATH = "database/oncopharm.db"
LOG_PATH = "data/processed/decisoes_clinicas.txt"

# --- Funções Backend ---
def get_data_from_sql():
    if not os.path.exists(DB_PATH): return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        # Recupera dados ordenados pelo mais recente
        df = pd.read_sql("SELECT person_id as 'ID', episode_source_value as 'Detalhes' FROM episode ORDER BY episode_id DESC LIMIT 50", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def save_decision_log(paciente_id, acao, notas, nlp_alerts):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] PACIENTE: {paciente_id}\n"
        f"ACAO: {acao}\n"
        f"ALERTA IA: {nlp_alerts}\n"
        f"EVOLUCAO: {notas}\n"
        f"{'-'*60}\n"
    )
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

# --- Interface Principal ---
st.title("🏥 OncoPharm: Plataforma de Oncologia de Precisão")
st.markdown("### 🔌 Conexão: SQL + NLP + Interoperabilidade (Tasy/Notivisa)")
st.markdown("---")

# Carrega dados
df_sql = get_data_from_sql()
paciente_selecionado = "N/A"
detalhes_paciente = "Aguardando integração..."

# Layout Superior
col_dados, col_intel = st.columns([1, 2])

with col_dados:
    st.subheader("🗄️ Prontuário (SQL)")
    if not df_sql.empty:
        st.dataframe(df_sql.head(10), use_container_width=True, hide_index=True)
        # Pega o paciente mais recente (topo da lista)
        paciente_selecionado = df_sql.iloc[0]['ID']
        detalhes_paciente = df_sql.iloc[0]['Detalhes']
        st.info(f"Paciente em Foco: {paciente_selecionado}")
    else:
        st.warning("Banco de dados vazio. Inicie o simulador Tasy.")

with col_intel:
    st.subheader("🧠 Inteligência Clínica Multi-modal")
    tab1, tab2, tab3, tab4 = st.tabs(["📉 PK (Dose)", "🔮 Risco (IA)", "📝 Monitor NLP", "🚨 ANVISA"])
    
    with tab1:
        if os.path.exists("simulacao_pk.png"): 
            st.image(Image.open("simulacao_pk.png"), width=400, caption="Simulação Farmacocinética")
        else: 
            st.warning("Execute o modelo PK primeiro.")
        
    with tab2:
        if os.path.exists("curva_sobrevivencia_toxicidade.png"): 
            st.image(Image.open("curva_sobrevivencia_toxicidade.png"), width=400, caption="Curva de Risco CoxPH")
        else: 
            st.warning("Execute o modelo de Risco primeiro.")

    # Monitoramento de Texto (NLP)
    with tab3:
        st.info("O sistema monitora a evolução clínica digitada abaixo em tempo real.")

    # Integração ANVISA
    with tab4:
        st.markdown("##### 🏛️ Notificação Compulsória")
        if st.button("🚀 PREPARAR NOTIVISA", type="primary"):
            dados_incidente = {
                "patient_id": paciente_selecionado,
                "event": "Detectado via NLP (Vide notas)",
                "grade": "Verificar",
                "notes": "Vide evolução clínica",
                "date": str(datetime.date.today())
            }
            relatorio = st.session_state['notivisa_bot'].generate_copy_paste_report(dados_incidente)
            st.session_state['notivisa_report'] = relatorio
            st.session_state['notivisa_bot'].open_portal()
            st.success("Portal ANVISA aberto. Copie os dados abaixo.")
            
        if st.session_state['notivisa_report']:
            st.text_area("📋 Dados para Copiar:", st.session_state['notivisa_report'], height=150)

# --- ÁREA DE DECISÃO DIDÁTICA (RESTAURADA) ---
st.markdown("---")
st.header("📝 Farmácia Clínica: Tomada de Decisão & Registro")

# Container visual para destacar a área de ação
with st.container():
    c1, c2, c3 = st.columns([1, 2, 1])
    
    # Coluna 1: Intervenção
    with c1:
        st.markdown("**1. Ajuste de Dose**")
        decisao_dose = st.radio(
            "Selecione a conduta:",
            ("Manter Dose Prescrita", 
             "Reduzir 20% (Preventivo)", 
             "Reduzir 50% (Toxicidade Grave)", 
             "Suspender Ciclo"),
            index=1
        )
    
    # Coluna 2: Evolução (Com NLP em tempo real)
    with c2:
        st.markdown("**2. Acompanhamento Clínico**")
        notas_clinicas = st.text_area(
            "Justificativa e Notas de Evolução:",
            value=f"Paciente {paciente_selecionado}. Detalhes Clinicos: {detalhes_paciente}.",
            height=130
        )
        
        # O NLP roda aqui em tempo real
        aes_detectados = st.session_state['nlp_engine'].analyze_text(notas_clinicas)
        if aes_detectados:
            termos = [x['termo'] for x in aes_detectados]
            st.caption(f"🔴 Termos de risco identificados: {', '.join(termos)}")
            st.toast(f"Alerta NLP: {termos}", icon="⚠️")
        
    # Coluna 3: Botão de Ação
    with c3:
        st.markdown("**3. Registro**")
        st.write("") 
        st.write("")
        
        # Botão grande e vermelho para registrar
        if st.button("💾 REGISTRAR DECISÃO", type="primary", use_container_width=True):
            if paciente_selecionado != "N/A":
                save_decision_log(
                    paciente_selecionado, 
                    decisao_dose, 
                    notas_clinicas, 
                    str([x['termo'] for x in aes_detectados])
                )
                st.success("✅ Intervenção registrada no prontuário!")
                st.balloons()
            else:
                st.error("Nenhum paciente selecionado.")

st.markdown("---")
st.caption("OncoPharm CDSS v2.2 (Stable) | Governança: DVC + SQL | ANVISA Integrada")
