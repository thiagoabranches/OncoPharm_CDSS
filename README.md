# 🏥 OncoPharm CDSS: Plataforma de Oncologia de Precisão

Esta plataforma é uma implementação de referência baseada na revisão sistemática *"Arquitetura de Dados, Inteligência Artificial e Governança Computacional na Farmácia Clínica Oncológica"*[cite: 1].

O sistema integra dados estruturados (SQL/OMOP) [cite: 73, 75], modelagem farmacocinética (PK/PD) [cite: 53] e inteligência artificial para suporte à decisão clínica (CDSS).

## 🚀 Funcionalidades Implementadas

1.  **Prontuário Eletrônico OMOP**: Persistência de dados clínicos usando o padrão internacional *Common Data Model* com Extensão de Oncologia[cite: 77].
2.  **Farmacocinética Computacional**: Simulação de ajuste de dose (MIPD) baseada em modelos de um compartimento e visualização de decaimento[cite: 66].
3.  **Predição de Risco (IA)**: Algoritmos de análise de sobrevivência (*Cox Proportional Hazards*) para prever toxicidade em tempo-até-evento[cite: 111].
4.  **Processamento de Linguagem Natural (NLP)**: Monitoramento ativo de notas clínicas para detecção de eventos adversos, atuando como "triagem de alta revocação"[cite: 45].
5.  **Interoperabilidade**: Módulo adaptador para mensagens HL7 v2 (simulando Tasy/MV) e API REST.
6.  **Governança de Dados**: Controle de versão de código (Git) e dados (DVC) para garantir reprodutibilidade[cite: 137].

## 🛠️ Arquitetura Técnica

A solução segue uma arquitetura híbrida e modular, conforme proposto na literatura[cite: 10, 90]:

* **Linguagem Core**: Python 3.11+
* **Banco de Dados**: SQLite (Protótipo local) / Compatível com PostgreSQL
* **Interface**: Streamlit (Dashboard Interativo "Human-in-the-Loop" )

## 📦 Como Rodar o Projeto

### Pré-requisitos
* Python 3.11+
* Git Bash

### Instalação

1.  **Configurar ambiente:**
    \`\`\`bash
    python -m venv .venv
    source .venv/Scripts/activate
    pip install -r requirements.txt
    \`\`\`

2.  **Inicializar Banco de Dados (ETL):**
    \`\`\`bash
    python src/etl/02_load_to_sql.py
    \`\`\`

### Execução

Para iniciar o **Dashboard Clínico**:
\`\`\`bash
streamlit run src/app/dashboard.py
\`\`\`

Para rodar o **Simulador de Interoperabilidade** (em outro terminal):
\`\`\`bash
python src/integration/simulate_tasy.py
\`\`\`

---
*Desenvolvido como Prova de Conceito (PoC) para Farmácia Clínica Oncológica.*
