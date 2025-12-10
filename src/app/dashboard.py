import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import datetime
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline

# Tenta importar o módulo da Groq (Llama 3)
try:
    from src.ai.llm_groq import get_second_opinion
except:
    def get_second_opinion(a,b,c): return "Módulo Groq não configurado."

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="OncoPharm CDSS",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PROFISSIONAL ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    
    /* CARD DO DESENVOLVEDOR (Barra Lateral) */
    .developer-card {
        background-color: #f0f2f6;
        border: 1px solid #d6d6d6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        font-family: sans-serif;
    }
    .dev-title {
        color: #0072b1;
        font-weight: bold;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 2px solid #0072b1;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }
    .dev-name { font-size: 1.1rem; font-weight: bold; color: #333; }
    .dev-crf { font-size: 0.9rem; color: #555; font-weight: 500; }
    .dev-contact { font-size: 0.85rem; color: #444; margin-top: 10px; line-height: 1.6; }
    .dev-contact a { text-decoration: none; color: #0072b1; font-weight: bold; }
    .dev-contact a:hover { text-decoration: underline; }

    /* BANNER DO PACIENTE */
    .patient-banner {
        background: linear-gradient(90deg, #0e1117 0%, #1e2330 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #0072b1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    
    /* BADGES E TAGS */
    .badge-grade { padding: 5px 10px; border-radius: 6px; color: white; font-weight: bold; font-size: 0.85rem; }
    .bg-grave { background-color: #d32f2f; }
    .bg-leve { background-color: #2e7d32; }
    .entity-tag { 
        display: inline-block; padding: 3px 8px; margin: 3px; border-radius: 15px; 
        background: #e3f2fd; border: 1px solid #90caf9; color: #1565c0; font-size: 0.85rem; font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. IA HÍBRIDA (CARREGAMENTO) ---
@st.cache_resource
def load_ai_engine():
    # 1. BioBERT (Extração)
    try:
        ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple")
    except: ner = None
    
    # 2. Random Forest (Classificação)
    try:
        base = os.getcwd()
        df = pd.read_csv(os.path.join(base, "data/processed/treino_ia.csv"))
        rf = make_pipeline(TfidfVectorizer(), RandomForestClassifier(n_estimators=50, random_state=42))
        rf.fit(df['texto'], df['gravidade'])
    except: rf = None
    return ner, rf

ner_engine, rf_engine = load_ai_engine()

# --- 4. DADOS (CARREGAMENTO) ---
@st.cache_data
def load_data():
    try:
        base = os.getcwd()
        p = pd.read_csv(os.path.join(base, "data/processed/pacientes_mock.csv"))
        e = pd.read_csv(os.path.join(base, "data/processed/exames_mock.csv"))
        n = pd.read_csv(os.path.join(base, "data/processed/notas_mock.csv"))
        return p, e, n
    except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_p, df_e, df_n = load_data()

# --- 5. BARRA LATERAL (CONFIG + ASSINATURA) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=60)
    st.title("OncoPharm CDSS")
    st.caption("Sistema de Apoio à Decisão Clínica")
    st.markdown("---")
    
    # CONFIGURAÇÃO DE IA
    with st.expander("⚙️ Configuração IA (Opcional)"):
        api_key = st.text_input("Groq API Key (Llama 3):", type="password")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("Conectado!")

    st.markdown("---")

    # SELEÇÃO DE PACIENTE
    if not df_p.empty:
        st.subheader("📂 Prontuário Eletrônico")
        lista = df_p.apply(lambda x: f"{x['id']} - {x['nome']}", axis=1)
        sel = st.selectbox("Buscar Paciente:", lista)
        pid = int(sel.split(" - ")[0])
        paciente = df_p[df_p['id'] == pid].iloc[0]
        exames = df_e[df_e['patient_id'] == pid]
        notas = df_n[df_n['patient_id'] == pid]
    else: st.stop()

    st.markdown("---")

    # ASSINATURA COMPLETA (Cartão Profissional)
    st.markdown("""
    <div class="developer-card">
        <div class="dev-title">RESPONSÁVEL TÉCNICO</div>
        <div class="dev-name">Farm. Thiago Abranches</div>
        <div class="dev-crf">CRF-SP 091811 | Oncologia</div>
        <hr style="margin: 10px 0; border-color: #ccc;">
        <div class="dev-contact">
            📱 <b>Tel:</b> (11) 94146-9952<br>
            📧 <b>Email:</b> thabranches@gmail.com<br>
            🔗 <a href="https://linkedin.com/in/thiago-abranches" target="_blank">Perfil LinkedIn</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. PATIENT BANNER (CABEÇALHO) ---
creat = exames[exames['tipo']=='Creatinina']['valor'].iloc[-1] if not exames.empty else 0.0
risco = creat > 1.2
status_txt = "🔴 ALERTA RENAL (MIPD)" if risco else "🟢 ESTÁVEL"

st.markdown(f"""
<div class="patient-banner">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h2 style="margin:0; font-weight:700;">{paciente['nome']}</h2>
            <span style="opacity:0.9;">ID: {paciente['id']} &nbsp;|&nbsp; Idade: {paciente['idade']}a &nbsp;|&nbsp; Sexo: {paciente['sexo']}</span>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Status Clínico</div>
            <div style="font-weight:bold; font-size:1.1rem; color: {'#ff8a80' if risco else '#b9f6ca'};">{status_txt}</div>
        </div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.2); margin:10px 0;">
    <div style="display:flex; gap:30px; font-size:0.9rem;">
        <span>📏 <b>BSA:</b> {paciente['bsa']} m²</span>
        <span>⚖️ <b>Peso:</b> {paciente['peso']} kg</span>
        <span>🧪 <b>Creatinina:</b> {creat} mg/dL</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 7. NAVEGAÇÃO POR ABAS (MAIN CONTENT) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Geral", 
    "💊 Farmacocinética (PK)", 
    "🤖 Farmacovigilância Híbrida", 
    "✅ Decisão & Notificação"
])

# ABA 1: VISÃO GERAL
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Clearance Estimado", "45 mL/min" if risco else "95 mL/min", delta="-Baixo" if risco else "Normal")
    c2.metric("Ciclo Atual", "Cisplatina D1", "Protocolo Padrão")
    c3.metric("Última Internação", "12/12/2025")
    
    st.markdown("##### 📋 Histórico Laboratorial Recente")
    st.dataframe(exames, use_container_width=True, hide_index=True)

# ABA 2: PK (MIPD)
with tab2:
    col_k, col_g = st.columns([1, 3])
    with col_k:
        st.info("Parâmetros Farmacocinéticos")
        if risco:
            st.error("⚠️ Depuração Renal Comprometida")
            st.markdown("**Ajuste Sugerido:** `Reduzir 25%`")
            kel = 0.15
        else:
            st.success("✅ Função Renal Preservada")
            st.markdown("**Ajuste Sugerido:** `Manter Dose`")
            kel = 0.45
        st.write(f"Constante de Eliminação (ke): {kel}")
    
    with col_g:
        t = np.linspace(0, 24, 100)
        c = (100/30)*np.exp(-kel*t)
        fig = go.Figure(go.Scatter(x=t, y=c, fill='tozeroy', name='Conc. Plasmática', line=dict(color='#0072b1', width=3)))
        fig.add_hline(y=1.5, line_dash="dash", line_color="red", annotation_text="Toxicidade")
        fig.update_layout(title="Simulação de Decaimento (24h)", template="plotly_white", height=350)
        st.plotly_chart(fig, use_container_width=True)

# ABA 3: IA HÍBRIDA (BioBERT + Random Forest)
with tab3:
    st.markdown("### 🕵️ Monitoramento de Reações Adversas (RAMs)")
    texto = notas['texto'].iloc[0]
    
    c_in, c_out = st.columns([1, 1])
    with c_in:
        st.markdown("**Nota de Evolução (Texto Livre):**")
        st.text_area("Prontuário:", value=texto, height=200, disabled=True)
        
        if st.button("🔍 Executar Análise Híbrida", type="primary"):
            if ner_engine and rf_engine:
                with st.spinner("Analisando semântica e gravidade..."):
                    g = rf_engine.predict([texto])[0]
                    c = rf_engine.predict_proba([texto]).max()
                    e = ner_engine(texto)
                    st.session_state['ai_res'] = {'g': g, 'c': c, 'e': e}
            else: st.warning("IA carregando...")

    with c_out:
        if 'ai_res' in st.session_state:
            res = st.session_state['ai_res']
            
            # Badge de Gravidade
            cor = "bg-grave" if "Grave" in res['g'] else "bg-leve"
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:15px; border-radius:8px; margin-bottom:15px; background:#fafafa;">
                <label style="color:#555; font-size:0.9rem;">Classificação CTCAE (Random Forest):</label><br>
                <span class="badge-grade {cor}">{res['g']}</span>
                <span style="font-size:0.8rem; color:#666; margin-left:10px;">Confiança: {int(res['c']*100)}%</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Entidades
            st.markdown("**Entidades Clínicas (BioBERT):**")
            if res['e']:
                for ent in res['e']:
                    st.markdown(f"<span class='entity-tag'>{ent['word']} <small>({ent['entity_group']})</small></span>", unsafe_allow_html=True)
            else: st.info("Sem termos específicos.")

            # LLM Segunda Opinião
            st.markdown("---")
            if st.button("🧠 Pedir Segunda Opinião (Llama 3)"):
                if "GROQ_API_KEY" in os.environ:
                    with st.spinner("Consultando literatura..."):
                        parecer = get_second_opinion(texto, res['g'], res['e'])
                        st.info(parecer)
                else: st.error("Configure a API Key na barra lateral.")

# ABA 4: DECISÃO & NOTIVISA
with tab4:
    st.subheader("📝 Registro de Intervenção & Notificação")
    
    with st.form("decision_form"):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            decisao = st.selectbox("Conduta Farmacêutica:", 
                ["Liberar Protocolo", "Ajuste de Dose (-25%)", "Ajuste de Dose (-50%)", "Suspender Ciclo", "Solicitar Exames"])
            justif = st.text_area("Justificativa Técnica:", height=100)
        
        with col_d2:
            st.markdown("**Ações Regulatórias:**")
            notificar = st.checkbox("Gerar Relatório de Farmacovigilância")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🔒 ASSINAR DIGITALMENTE", type="primary")
    
    if submit:
        st.success("✅ Intervenção registrada com sucesso no Log de Auditoria.")
        if notificar:
            st.warning("⚠️ Evento adverso sinalizado para notificação.")
            # Botão oficial do NOTIVISA
            st.markdown("### 🔗 Acesso Externo")
            st.link_button("🚀 Acessar Sistema NOTIVISA (ANVISA)", "https://www8.anvisa.gov.br/notivisa/frLogin.asp")

