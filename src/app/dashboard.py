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

# Importa o módulo Groq que acabamos de criar
# (Precisamos garantir que o python ache o caminho, por isso o try/except no import)
try:
    from src.ai.llm_groq import get_second_opinion
except:
    # Função dummy se der erro no import
    def get_second_opinion(a,b,c): return "Módulo Groq não encontrado."

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="OncoPharm CDSS", layout="wide", page_icon="⚕️", initial_sidebar_state="expanded")

# --- 2. CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    .developer-card { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; margin-bottom: 20px; font-size: 0.9rem; }
    .dev-header { color: #0072b1; font-weight: bold; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px; }
    .dev-name { font-weight: bold; font-size: 1.1rem; color: #333; }
    .patient-banner { background-color: #0e1117; color: white; padding: 15px; border-radius: 8px; border-left: 5px solid #0072b1; margin-bottom: 20px; }
    .badge-grade { padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.8rem; }
    .bg-grave { background-color: #d32f2f; } .bg-leve { background-color: #388e3c; }
    .entity-tag { display: inline-block; padding: 2px 6px; margin: 2px; border-radius: 10px; background: #e3f2fd; border: 1px solid #90caf9; font-size: 0.85rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. IA HÍBRIDA (BioBERT + RF) ---
@st.cache_resource
def load_ai_engine():
    try:
        ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple")
    except: ner = None
    try:
        base = os.getcwd()
        df = pd.read_csv(os.path.join(base, "data/processed/treino_ia.csv"))
        rf = make_pipeline(TfidfVectorizer(), RandomForestClassifier(n_estimators=50, random_state=42))
        rf.fit(df['texto'], df['gravidade'])
    except: rf = None
    return ner, rf

ner_engine, rf_engine = load_ai_engine()

# --- 4. DADOS ---
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("⚕️ OncoPharm CDSS")
    
    # CONFIG API GROQ (Segurança)
    with st.expander("🔑 Configurar IA Generativa"):
        groq_key = st.text_input("Cole sua API Key da Groq:", type="password")
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
            st.success("Chave configurada!")
    
    st.markdown("""
    <div class="developer-card">
        <div class="dev-header">Desenvolvedor Responsável</div>
        <span class="dev-name">Farm. Thiago Abranches</span>
        <span style="color:#666; font-size:0.9rem">CRF-SP 091811</span>
    </div>
    """, unsafe_allow_html=True)
    
    if not df_p.empty:
        st.subheader("📂 Prontuário")
        lista = df_p.apply(lambda x: f"{x['id']} - {x['nome']}", axis=1)
        sel = st.selectbox("Selecione:", lista)
        pid = int(sel.split(" - ")[0])
        paciente = df_p[df_p['id'] == pid].iloc[0]
        exames = df_e[df_e['patient_id'] == pid]
        notas = df_n[df_n['patient_id'] == pid]
        st.markdown("---")
        nav = st.radio("Módulos:", ["Visão Geral", "PK (MIPD)", "Farmacovigilância 360º", "Decisão"])
    else: st.stop()

# --- 6. BANNER ---
creat = exames[exames['tipo']=='Creatinina']['valor'].iloc[-1] if not exames.empty else 0.0
risco = creat > 1.2
st.markdown(f"""
<div class="patient-banner">
    <h3 style="margin:0">{paciente['nome']}</h3>
    <span>ID: {paciente['id']} | Idade: {paciente['idade']} | <b>{'🔴 ALERTA RENAL' if risco else '🟢 ESTÁVEL'}</b></span>
</div>
""", unsafe_allow_html=True)

# --- 7. CONTEÚDO ---
if nav == "Visão Geral":
    c1,c2,c3 = st.columns(3)
    c1.metric("Creatinina", f"{creat} mg/dL")
    c2.metric("Clearance", "45 mL/min" if risco else "95 mL/min")
    c3.metric("Peso", f"{paciente['peso']} kg")
    st.dataframe(exames, use_container_width=True, hide_index=True)

elif nav == "PK (MIPD)":
    c1, c2 = st.columns([1, 3])
    with c1:
        st.info("Parâmetros Ajustados")
        st.write(f"**Constante ke:** {'0.15' if risco else '0.45'}")
        if risco: st.error("Reduzir Dose em 25%")
        else: st.success("Dose Padrão")
    with c2:
        t = np.linspace(0, 24, 100)
        c = (100/30)*np.exp(-(0.15 if risco else 0.45)*t)
        fig = go.Figure(go.Scatter(x=t, y=c, fill='tozeroy'))
        st.plotly_chart(fig, use_container_width=True)

elif nav == "Farmacovigilância 360º":
    st.subheader("🤖 IA Híbrida: BioBERT + Random Forest + Llama 3")
    texto = notas['texto'].iloc[0]
    
    c_in, c_out = st.columns([1,1])
    with c_in:
        st.text_area("Evolução:", value=texto, height=150, disabled=True)
        if st.button("🔍 Analisar (BioBERT + RF)", type="primary"):
            if ner_engine and rf_engine:
                with st.spinner("Processando..."):
                    grav = rf_engine.predict([texto])[0]
                    conf = rf_engine.predict_proba([texto]).max()
                    ents = ner_engine(texto)
                    st.session_state['ai_res'] = {'g': grav, 'c': conf, 'e': ents}
    
    with c_out:
        if 'ai_res' in st.session_state:
            res = st.session_state['ai_res']
            cor = "bg-grave" if "Grave" in res['g'] else "bg-leve"
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:15px; border-radius:8px;">
                <label>Classificação CTCAE:</label><br>
                <span class="badge-grade {cor}">{res['g']}</span> (Confiança: {int(res['c']*100)}%)
            </div>
            """, unsafe_allow_html=True)
            st.write("**Entidades:**")
            for e in res['e']: st.markdown(f"<span class='entity-tag'>{e['word']} ({e['entity_group']})</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("##### 🧠 Segunda Opinião (LLM)")
            if st.button("Consultar Dr. Llama-3 (Groq)"):
                if "GROQ_API_KEY" in os.environ:
                    with st.spinner("Gerando parecer clínico..."):
                        parecer = get_second_opinion(texto, res['g'], res['e'])
                        st.info(parecer)
                else:
                    st.warning("⚠️ Configure a API Key na barra lateral primeiro!")

elif nav == "Decisão":
    st.selectbox("Conduta:", ["Liberar", "Intervir"])
    st.text_area("Justificativa:")
    st.button("Assinar")
