# 🏥 OncoPharm CDSS: Plataforma de Oncologia de Precisão

Esta plataforma é uma implementação de referência baseada na revisão sistemática "Arquitetura de Dados, Inteligência Artificial e Governança Computacional na Farmácia Clínica Oncológica"[cite: 1].

O sistema integra dados estruturados (SQL/OMOP), modelagem farmacocinética (PK/PD) e inteligência artificial para suporte à decisão clínica (CDSS).

## 🚀 Funcionalidades

1.  **Prontuário Eletrônico OMOP**: Persistência de dados clínicos usando o padrão internacional *Common Data Model* com Extensão de Oncologia[cite: 75, 77].
2.  **Farmacocinética Computacional**: Simulação de ajuste de dose (MIPD) baseada em modelos de um compartimento[cite: 65].
3.  **Predição de Risco (IA)**: Algoritmos de análise de sobrevivência (*Cox Proportional Hazards*) para prever toxicidade[cite: 111].
4.  **Processamento de Linguagem Natural (NLP)**: Monitoramento ativo de notas clínicas para detecção de eventos adversos (Farmacovigilância).
5.  **Interoperabilidade**: Módulo adaptador para mensagens HL7 v2 (Tasy/MV) e API REST[cite: 94].

## 🛠️ Arquitetura Técnica

A solução segue uma arquitetura híbrida e modular[cite: 10, 90]:

* **Linguagem Core**: Python 3.11+
* **Banco de Dados**: SQLite (Protótipo) / PostgreSQL (Produção)
* **Interface**: Streamlit (Dashboard Interativo)
* **Governança**: 
    * Código: Git (Gitflow) [cite: 134]
    * Dados: DVC (Data Version Control) [cite: 139]

## 📦 Como Rodar o Projeto

### Pré-requisitos
* Python 3.11 ou superior
* Git Bash

### Instalação

1.  **Clone o repositório e entre na pasta:**
    \`\`\`bash
    git clone https://github.com/seu-usuario/OncoPharm_CDSS.git
    cd OncoPharm_CDSS
    \`\`\`

2.  **Crie e ative o ambiente virtual:**
    \`\`\`bash
    python -m venv .venv
    source .venv/Scripts/activate
    \`\`\`

3.  **Instale as dependências:**
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

4.  **Inicialize o Banco de Dados (ETL):**
    \`\`\`bash
    python src/etl/02_load_to_sql.py
    \`\`\`

### Execução

Para iniciar o Dashboard Clínico:
\`\`\`bash
streamlit run src/app/dashboard.py
\`\`\`

Para simular integração com Tasy (em outro terminal):
\`\`\`bash
python src/integration/simulate_tasy.py
\`\`\`

---
*Desenvolvido como Prova de Conceito (PoC) para Farmácia Clínica Oncológica.*
