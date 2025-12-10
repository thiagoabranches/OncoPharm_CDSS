import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import datetime
# Bibliotecas de IA (Robustez)
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline

# --- 1. CONFIGURAÇÃO ---
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
    /* Estilos do Desenvolvedor */
    .developer-card {
        background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px;
        padding: 15px; margin-bottom: 20px; font-size: 0.9rem;
    }
    .dev-header { color: #0072b1; font-weight: bold; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px; }
    .dev-name { font-weight: bold; font-size: 1.1rem; color: #333; }
    .dev-crf { color: #666; font-size: 0.9rem; margin-bottom: 10px; display: block; }
    /* Estilos de IA */
    .badge-grade { padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.8rem; }
    .bg-grave { background-color: #d32f2f; }
    .bg-leve { background-color: #388e3c; }
    .entity-tag { display: inline-block; padding: 2px 6px; margin: 2px; border-radius: 10px; background: #e3f2fd; border: 1px solid #90caf9; font-size: 0.85rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CARREGAMENTO DE MODELOS (IA HÍBRIDA) ---
@st.cache_resource
def load_ai_engine():
    """
    Implementa o Modelo Híbrido:
    1. BioBERT para Extração de Entidades (NER).
    2. Random Forest para Classificação de Gravidade (CTCAE).
    """
    # 1. BioBERT
    try:
        # Usa pipeline otimizado para CPU
        ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple")
    except:
        ner = None

    # 2. Random Forest (Treina rapidamente com os dados gerados)
    try:
        base = os.getcwd()
        df_treino = pd.read_csv(os.path.join(base, "data/processed/treino_ia.csv"))
        # Pipeline: Texto -> Vetor -> Classificador
        rf_pipeline = make_pipeline(TfidfVectorizer(), RandomForestClassifier(n_estimators=50, random_state=42))
        rf_pipeline.fit(df_treino['texto'], df_treino['gravidade'])
    except:
        rf_pipeline = None
        
    return ner, rf_pipeline

ner_engine, rf_engine = load_ai_engine()

# --- 4. CARREGAMENTO DE DADOS (FALLBACK) ---
@st.cache_data
def load_data():
    try:
        base = os.getcwd()
        p = pd.read_csv(os.path.join(base, "data/processed/pacientes_mock.csv"))
        e = pd.read_csv(os.path.join(base, "data/processed/exames_mock.csv"))
        n = pd.read_csv(os.path.join(base, "data/processed/notas_mock.csv"))
        return p, e, n
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_p, df_e, df_n = load_data()

# --- 5. SIDEBAR COM ASSINATURA ---
with st.sidebar:
    st.title("⚕️ OncoPharm CDSS")
    
    # ASSINATURA DO DESENVOLVEDOR (Mantida e em destaque)
    st.markdown("""
    <div class="developer-card">
        <div class="dev-header">Desenvolvedor Responsável</div>
        <span class="dev-name">Farm. Thiago Abranches</span>
        <span class="dev-crf">CRF-SP 091811</span>
        <hr style="margin: 8px 0; border-color: #dee2e6;">
        <div style="font-size: 0.85em;">
            📱 11 94146-9952<br>
            📧 thabranches@gmail.com<br>
            🔗 <a href="https://linkedin.com/in/thiago-abranches" target="_blank">LinkedIn Profile</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # SELEÇÃO DE PACIENTE
    if not df_p.empty:
        st.subheader("📂 Prontuário Eletrônico")
        lista = df_p.apply(lambda x: f"{x['id']} - {x['nome']}", axis=1)
        selecao = st.selectbox("Selecione:", lista)
        
        pid = int(selecao.split(" - ")[0])
        paciente = df_p[df_p['id'] == pid].iloc[0]
        exames = df_e[df_e['patient_id'] == pid]
        notas = df_n[df_n['patient_id'] == pid]
        
        st.markdown("---")
        nav = st.radio("Módulos:", ["Visão Geral", "Farmacocinética (PK)", "Farmacovigilância Híbrida (IA)", "Decisão Clínica"])
    else:
        st.stop()

# --- 6. PATIENT BANNER ---
creat = exames[exames['tipo']=='Creatinina']['valor'].iloc[-1] if not exames.empty else 0.0
risco = creat > 1.2
status_txt = "🔴 ALERTA RENAL" if risco else "🟢 ESTÁVEL"

st.markdown(f"""
<div style="background:#0e1117; color:white; padding:15px; border-radius:8px; border-left:5px solid #0072b1; margin-bottom:20px;">
    <h3 style="margin:0">{paciente['nome']}</h3>
    <span>ID: {paciente['id']} | Idade: {paciente['idade']} | BSA: {paciente['bsa']} m² | <b>{status_txt}</b></span>
</div>
""", unsafe_allow_html=True)

# --- 7. MÓDULOS ---

if nav == "Visão Geral":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Creatinina", f"{creat} mg/dL", delta="-Alto" if risco else "Ok", delta_color="inverse")
    c2.metric("Clearance Est.", "45 mL/min" if risco else "95 mL/min")
    c3.metric("Ciclo", "Cisplatina D1")
    c4.metric("Peso", f"{paciente['peso']} kg")
    st.markdown("##### Histórico Recente")
    st.dataframe(exames, use_container_width=True, hide_index=True)

elif nav == "Farmacocinética (PK)":
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown("#### Parâmetros MIPD")
        if risco:
            st.error("⚠️ Clearance Reduzido")
            st.write("**Sugestão:** Reduzir 25%")
            kel = 0.15
        else:
            st.success("✅ Função Normal")
            st.write("**Sugestão:** Dose Padrão")
            kel = 0.45
    with c2:
        t = np.linspace(0, 24, 100)
        c = (100/30)*np.exp(-kel*t)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=c, fill='tozeroy', name='Conc.'))
        fig.add_hline(y=1.5, line_dash="dash", line_color="red", annotation_text="Limiar Tóxico")
        fig.update_layout(title="Simulação PK (24h)", height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

elif nav == "Farmacovigilância Híbrida (IA)":
    st.subheader("🤖 Detecção e Classificação de RAMs (Modelo Híbrido)")
    st.markdown("Combinação de **BioBERT** (Extração) e **Random Forest** (Classificação de Gravidade).")
    
    texto = notas['texto'].iloc[0]
    
    col_input, col_res = st.columns([1, 1])
    
    with col_input:
        st.markdown("##### Evolução Clínica (Texto Livre)")
        st.text_area("Entrada:", value=texto, height=150, disabled=True)
        
        if st.button("🔍 Executar Análise de IA", type="primary"):
            if ner_engine and rf_engine:
                with st.spinner("Processando..."):
                    # 1. Classificação (Random Forest)
                    gravidade = rf_engine.predict([texto])[0]
                    confianca = rf_engine.predict_proba([texto]).max()
                    
                    # 2. Extração (BioBERT)
                    entidades = ner_engine(texto)
                    
                    st.session_state['ai_res'] = {'g': gravidade, 'c': confianca, 'e': entidades}
            else:
                st.error("Modelos ainda carregando... Aguarde um instante.")

    with col_res:
        if 'ai_res' in st.session_state:
            res = st.session_state['ai_res']
            
            # Badge de Gravidade
            cor = "bg-grave" if "Grave" in res['g'] else "bg-leve"
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:15px; border-radius:8px; margin-bottom:10px;">
                <label>Classificação CTCAE (Random Forest):</label><br>
                <span class="badge-grade {cor}">{res['g']}</span>
                <br><small>Confiança do Modelo: {int(res['c']*100)}%</small>
                <progress value="{int(res['c']*100)}" max="100" style="width:100%"></progress>
            </div>
            """, unsafe_allow_html=True)
            
            # Entidades BioBERT
            st.markdown("**Entidades Identificadas (BioBERT):**")
            if res['e']:
                for ent in res['e']:
                    st.markdown(f"<span class='entity-tag'>{ent['word']} ({ent['entity_group']})</span>", unsafe_allow_html=True)
            else:
                st.info("Nenhuma entidade específica detectada.")

elif nav == "Decisão Clínica":
    st.subheader("Assinatura e Conduta")
    with st.form("f"):
        c1, c2 = st.columns([2,1])
        with c1:
            st.selectbox("Conduta:", ["Liberar", "Ajustar", "Suspender"])
            st.text_area("Justificativa:")
            st.checkbox("Enviar para ANVISA (RPA)")
        with c2:
            st.markdown(f"**Responsável:**<br>Farm. Thiago Abranches<br>{datetime.now().strftime('%d/%m/%Y')}", unsafe_allow_html=True)
            if st.form_submit_button("🔒 ASSINAR"):
                st.success("Registrado com sucesso!")
