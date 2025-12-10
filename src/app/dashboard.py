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

# Importação Segura da Groq (com tratamento de erro)
try:
    from src.ai.llm_groq import get_second_opinion
except ImportError:
    def get_second_opinion(a,b,c): return "Módulo Groq não configurado."

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="OncoPharm CDSS",
    layout="wide",
    page_icon="💊",
    initial_sidebar_state="expanded"
)

# --- 2. LOGICA DE SEGURANÇA BLINDADA ---
# Tenta ler os segredos. Se der erro (porque está local), apenas segue em frente.
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        ia_status = "✅ IA Ativa (Licença do Sistema)"
        tem_chave = True
    else:
        ia_status = "⚠️ IA Offline (Configure a chave)"
        tem_chave = False
except Exception:
    # Se der erro de "Secrets not found" (comum no PC local), cai aqui
    ia_status = "⚠️ IA Offline (Modo Local)"
    tem_chave = False

# --- 3. CSS PROFISSIONAL ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    .main-header {
        background: linear-gradient(135deg, #0072b1 0%, #003d5c 100%);
        padding: 20px; border-radius: 10px; color: white; text-align: center;
        margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        display: flex; align-items: center; justify-content: center; gap: 20px;
    }
    .main-header h1 { margin: 0; font-size: 2.2rem; font-weight: 700; color: white; }
    .capsule-icon { font-size: 3rem; }
    .developer-card {
        background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px;
        padding: 15px; margin-bottom: 20px; text-align: left;
    }
    .dev-label { font-size: 0.75rem; color: #0072b1; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-bottom: 8px; }
    .dev-name { font-weight: bold; font-size: 1.1rem; color: #222; }
    .dev-contacts { font-size: 0.8rem; color: #444; margin-top: 10px; line-height: 1.5; }
    .dev-contacts a { color: #0072b1; text-decoration: none; font-weight: 600; }
    .patient-banner { background-color: #1e2330; color: white; padding: 15px 20px; border-radius: 8px; border-left: 5px solid #00c853; margin-bottom: 20px; }
    .badge-grade { padding: 4px 10px; border-radius: 4px; color: white; font-weight: bold; }
    .bg-grave { background-color: #d32f2f; } .bg-leve { background-color: #388e3c; }
    .entity-tag { display: inline-block; padding: 2px 8px; margin: 2px; border-radius: 12px; background: #e3f2fd; border: 1px solid #90caf9; color:#0d47a1; font-size: 0.85rem; }
    </style>
""", unsafe_allow_html=True)

# --- 4. CARREGAMENTO DE MODELOS E DADOS ---
@st.cache_resource
def load_ai():
    try: 
        ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple")
    except: 
        ner = None
    
    # Random Forest com dados de exemplo embutidos (Fallback)
    try:
        base = os.getcwd()
        path = os.path.join(base, "data/processed/treino_ia.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            # Dados de treino na memória se não achar arquivo
            data_train = {"texto": ["Dor leve", "Dor intensa e vomitos", "Neutropenia febril", "Sem queixas"], 
                          "gravidade": ["Grau 1 (Leve)", "Grau 3/4 (Grave)", "Grau 3/4 (Grave)", "Grau 0"]}
            df = pd.DataFrame(data_train)
            
        rf = make_pipeline(TfidfVectorizer(), RandomForestClassifier(n_estimators=50))
        rf.fit(df['texto'], df['gravidade'])
    except: 
        rf = None
    return ner, rf

ner_engine, rf_engine = load_ai()

@st.cache_data
def load_data():
    # Tenta carregar do disco. Se falhar, carrega da memória (Blindagem)
    try:
        base = os.getcwd()
        p = pd.read_csv(os.path.join(base, "data/processed/pacientes_mock.csv"))
        e = pd.read_csv(os.path.join(base, "data/processed/exames_mock.csv"))
        n = pd.read_csv(os.path.join(base, "data/processed/notas_mock.csv"))
        return p, e, n
    except Exception:
        # DADOS DE EMERGÊNCIA (FALLBACK)
        p = pd.DataFrame([
            {"id": 1001, "nome": "Maria Silva (Demo)", "idade": 45, "sexo": "F", "peso": 60.0, "bsa": 1.65, "status": "Tratamento"},
            {"id": 1002, "nome": "João Santos (Demo)", "idade": 68, "sexo": "M", "peso": 75.0, "bsa": 1.88, "status": "Risco Elevado"}
        ])
        e = pd.DataFrame([
            {"patient_id": 1001, "tipo": "Creatinina", "valor": 0.8},
            {"patient_id": 1002, "tipo": "Creatinina", "valor": 1.9}
        ])
        n = pd.DataFrame([
            {"patient_id": 1001, "texto": "Paciente refere fadiga leve, mantendo atividades."},
            {"patient_id": 1002, "texto": "Apresenta sinais de nefrotoxicidade aguda e oligúria severa."}
        ])
        return p, e, n

df_p, df_e, df_n = load_data()

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.markdown("""
    <div class="developer-card">
        <div class="dev-label">Desenvolvedor Responsável</div>
        <div class="dev-name">Farm. Thiago Abranches</div>
        <div class="dev-crf">CRF-SP 091811 | Oncologia</div>
        <div class="dev-contacts">
            📱 (11) 94146-9952<br>
            📧 thabranches@gmail.com<br>
            🔗 <a href="https://linkedin.com/in/thiago-abranches" target="_blank">LinkedIn Profile</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("⚙️ Configuração do Sistema"):
        st.caption(f"Status: {ia_status}")
        # Se não tem chave salva (modo local), pede a chave manualmente
        if not tem_chave:
            api_key = st.text_input("Cole sua Groq API Key:", type="password")
            if api_key: os.environ["GROQ_API_KEY"] = api_key

    if not df_p.empty:
        st.subheader("📂 Prontuários")
        lista = df_p.apply(lambda x: f"{x['id']} - {x['nome']}", axis=1)
        sel = st.selectbox("Buscar Paciente:", lista)
        pid = int(sel.split(" - ")[0])
        paciente = df_p[df_p['id'] == pid].iloc[0]
        exames = df_e[df_e['patient_id'] == pid]
        notas = df_n[df_n['patient_id'] == pid]
    else:
        st.error("Erro crítico: Dados não carregados.")
        st.stop()

# --- 6. HEADER ---
st.markdown("""
<div class="main-header">
    <div class="capsule-icon">💊</div>
    <div>
        <h1>OncoPharm CDSS</h1>
        <p>Sistema de Apoio à Decisão Clínica em Oncologia de Precisão</p>
    </div>
</div>
""", unsafe_allow_html=True)

creat = exames[exames['tipo']=='Creatinina']['valor'].iloc[-1] if not exames.empty else 0.0
risco = creat > 1.2
st.markdown(f"""
<div class="patient-banner" style="border-left-color: {'#ff5252' if risco else '#00c853'};">
    <h3 style="margin:0">{paciente['nome']}</h3>
    <span>ID: {paciente['id']} | Idade: {paciente['idade']}a | <b>{'🔴 ALERTA RENAL' if risco else '🟢 ESTÁVEL'}</b></span>
</div>
""", unsafe_allow_html=True)

# --- 7. ABAS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "💊 Farmacocinética", "🤖 Farmacovigilância Híbrida", "✅ Decisão"])

with tab1:
    c1,c2,c3 = st.columns(3)
    c1.metric("Creatinina", f"{creat} mg/dL")
    c2.metric("Clearance", "45 mL/min" if risco else "95 mL/min")
    c3.metric("Peso", f"{paciente['peso']} kg")
    st.dataframe(exames, use_container_width=True, hide_index=True)

with tab2:
    c1, c2 = st.columns([1,3])
    with c1:
        st.info("Ajuste MIPD")
        if risco: st.error("Reduzir 25%"); kel=0.15
        else: st.success("Dose Padrão"); kel=0.45
    with c2:
        t = np.linspace(0, 24, 100)
        c = (100/30)*np.exp(-kel*t)
        fig = go.Figure(go.Scatter(x=t, y=c, fill='tozeroy', name='Conc.'))
        fig.add_hline(y=1.5, line_dash="dash", line_color="red")
        fig.update_layout(title="Simulação 24h", height=350)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 🕵️ Análise de Texto (BioBERT + RF)")
    texto = notas['texto'].iloc[0]
    c1, c2 = st.columns(2)
    with c1:
        st.text_area("Evolução:", value=texto, height=180, disabled=True)
        if st.button("🔍 Analisar"):
            if ner_engine and rf_engine:
                with st.spinner("Processando..."):
                    g = rf_engine.predict([texto])[0]
                    c = rf_engine.predict_proba([texto]).max()
                    e = ner_engine(texto)
                    st.session_state['ai_res'] = {'g':g, 'c':c, 'e':e}
            else: st.warning("Modelo IA carregando...")
    with c2:
        if 'ai_res' in st.session_state:
            res = st.session_state['ai_res']
            bg = "bg-grave" if "Grave" in res['g'] else "bg-leve"
            st.markdown(f"<span class='badge-grade {bg}'>{res['g']}</span> (Conf: {int(res['c']*100)}%)", unsafe_allow_html=True)
            st.write(res['e'])
            if st.button("🧠 Segunda Opinião (Groq)"):
                if "GROQ_API_KEY" in os.environ:
                    with st.spinner("Consultando..."):
                        op = get_second_opinion(texto, res['g'], res['e'])
                        st.info(op)
                else: st.warning("Chave de API não configurada.")

with tab4:
    st.selectbox("Conduta:", ["Liberar", "Intervir"])
    st.text_area("Justificativa:")
    if st.button("🔒 Assinar Digitalmente"):
        st.success("Registrado!")
    st.markdown("---")
    st.link_button("🚀 Notificar no NOTIVISA", "https://www8.anvisa.gov.br/notivisa/frLogin.asp")