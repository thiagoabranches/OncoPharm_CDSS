import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="OncoPharm CDSS",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (VISUAL) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    .developer-card {
        background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px;
        padding: 15px; margin-bottom: 20px; font-size: 0.9rem;
    }
    .dev-header { color: #0072b1; font-weight: bold; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px; }
    .dev-name { font-weight: bold; font-size: 1.1rem; color: #333; }
    .dev-crf { color: #666; font-size: 0.9rem; margin-bottom: 10px; display: block; }
    .patient-banner {
        background-color: #0e1117; color: white; padding: 15px;
        border-radius: 8px; border-left: 5px solid #0072b1; margin-bottom: 20px;
    }
    div[data-testid="stMetric"] { background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DADOS (COM FALLBACK AUTOMÁTICO) ---
@st.cache_data
def load_data():
    # Tenta carregar do arquivo. Se falhar, GERA NA HORA.
    try:
        base = os.getcwd()
        p = pd.read_csv(os.path.join(base, "data/processed/pacientes_mock.csv"))
        e = pd.read_csv(os.path.join(base, "data/processed/exames_mock.csv"))
        n = pd.read_csv(os.path.join(base, "data/processed/notas_mock.csv"))
        return p, e, n
    except Exception:
        # --- FALLBACK: DADOS NA MEMÓRIA (SEGURANÇA) ---
        p = pd.DataFrame([
            {"id": 1001, "nome": "Maria Silva", "idade": 45, "sexo": "F", "peso": 60.0, "bsa": 1.65, "status": "Tratamento"},
            {"id": 1002, "nome": "João Santos", "idade": 68, "sexo": "M", "peso": 75.0, "bsa": 1.88, "status": "Alerta Renal"},
            {"id": 1003, "nome": "Ana Costa", "idade": 52, "sexo": "F", "peso": 68.0, "bsa": 1.70, "status": "Monitoramento"}
        ])
        e = pd.DataFrame([
            {"patient_id": 1001, "tipo": "Creatinina", "valor": 0.8},
            {"patient_id": 1002, "tipo": "Creatinina", "valor": 1.9},
            {"patient_id": 1003, "tipo": "Creatinina", "valor": 0.9}
        ])
        n = pd.DataFrame([
            {"patient_id": 1001, "texto": "Sem queixas."},
            {"patient_id": 1002, "texto": "Fadiga e diurese escurecida."},
            {"patient_id": 1003, "texto": "Relata tinnitus (zumbido) e rash cutâneo."}
        ])
        return p, e, n

df_p, df_e, df_n = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚕️ OncoPharm CDSS")
    
    # ASSINATURA (SEMPRE APARECE)
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
    
    # NAVEGAÇÃO
    st.subheader("📂 Prontuário")
    lista = df_p.apply(lambda x: f"{x['id']} - {x['nome']}", axis=1)
    selecao = st.selectbox("Selecione:", lista)
    
    pid = int(selecao.split(" - ")[0])
    paciente = df_p[df_p['id'] == pid].iloc[0]
    exames = df_e[df_e['patient_id'] == pid]
    notas = df_n[df_n['patient_id'] == pid]
    
    st.markdown("---")
    nav = st.radio("Módulos:", ["Visão Geral", "Farmacocinética", "Vigilância (NLP)", "Decisão Clínica"])

# --- 5. PATIENT BANNER ---
creat = exames[exames['tipo']=='Creatinina']['valor'].iloc[-1] if not exames.empty else 0.0
risco = creat > 1.2
status_txt = "🔴 ALERTA RENAL" if risco else "🟢 ESTÁVEL"

st.markdown(f"""
<div class="patient-banner">
    <h3 style="margin:0">{paciente['nome']}</h3>
    <span>ID: {paciente['id']} | Idade: {paciente['idade']} | BSA: {paciente['bsa']} m² | <b>{status_txt}</b></span>
</div>
""", unsafe_allow_html=True)

# --- 6. CONTEÚDO ---
if nav == "Visão Geral":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Creatinina", f"{creat} mg/dL", delta="-Alto" if risco else "Ok", delta_color="inverse")
    c2.metric("Clearance Est.", "45 mL/min" if risco else "95 mL/min")
    c3.metric("Ciclo", "Cisplatina D1")
    c4.metric("Peso", f"{paciente['peso']} kg")
    st.dataframe(exames, use_container_width=True, hide_index=True)

elif nav == "Farmacocinética":
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
        fig.add_hline(y=1.5, line_dash="dash", line_color="red")
        fig.update_layout(title="Simulação 24h", height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

elif nav == "Vigilância (NLP)":
    st.subheader("Análise de Texto")
    texto = notas['texto'].iloc[0]
    termos = ["neutropenia", "tinnitus", "nefrotoxicidade", "rash", "oligúria", "zumbido"]
    
    html = texto
    achou = []
    for t in termos:
        if t in texto.lower():
            achou.append(t)
            html = html.replace(t, f"<span style='background:#fff59d; font-weight:bold;'>{t}</span>")
    
    c1, c2 = st.columns([2,1])
    with c1: st.markdown(f"<div style='background:white; padding:15px; border:1px solid #ddd; border-radius:5px;'>{html}</div>", unsafe_allow_html=True)
    with c2: 
        if achou: 
            for x in achou: st.error(f"🚨 {x.upper()}")
        else: st.success("Nenhum termo crítico.")

elif nav == "Decisão Clínica":
    st.subheader("Assinatura e Conduta")
    with st.form("f"):
        c1, c2 = st.columns([2,1])
        with c1:
            st.selectbox("Conduta:", ["Liberar", "Ajustar", "Suspender"])
            st.text_area("Justificativa:")
        with c2:
            st.markdown(f"**Responsável:**<br>Farm. Thiago Abranches<br>{datetime.now().strftime('%d/%m/%Y')}", unsafe_allow_html=True)
            if st.form_submit_button("🔒 ASSINAR"):
                st.success("Registrado com sucesso!")
