import os
from groq import Groq
import streamlit as st

def get_second_opinion(texto_clinico, gravidade, entidades):
    """
    Usa a API gratuita da Groq (Llama 3) para gerar uma segunda opinião clínica.
    """
    # Tenta pegar a chave dos segredos do Streamlit ou usa uma hardcoded para teste LOCAL
    # ATENÇÃO: Para o Github, o ideal é usar st.secrets. 
    # Para facilitar seu teste agora, você pode colar sua chave abaixo temporariamente.
    api_key = os.environ.get("GROQ_API_KEY") 
    
    # SE VOCÊ NÃO TIVER CONFIGURADO ENV VARS, COLOQUE SUA CHAVE ABAIXO (Cuidado ao commitar)
    if not api_key:
        # api_key = "gsk_..." <--- Coloque sua chave aqui se der erro
        return "⚠️ Erro: API Key da Groq não encontrada. Configure as variáveis de ambiente."

    client = Groq(api_key=api_key)

    system_prompt = """
    Você é um Oncologista Sênior e Farmacêutico Clínico. 
    Analise o caso focando em: 1. Validação da gravidade; 2. Manejo de sintomas; 3. Segurança da Cisplatina.
    Responda em Português (Brasil). Seja conciso e use tópicos.
    """

    user_prompt = f"""
    CASO CLÍNICO: "{texto_clinico}"
    
    DADOS DO SISTEMA:
    - Entidades encontradas: {entidades}
    - Classificação Automática: {gravidade}
    
    Por favor, forneça uma segunda opinião estruturada.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="llama3-70b-8192", # Modelo Gratuito e Muito Inteligente
            temperature=0.2,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro na conexão com Groq: {str(e)}"
