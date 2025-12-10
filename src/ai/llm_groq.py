import os
from groq import Groq
import streamlit as st

def get_second_opinion(texto_clinico, gravidade, entidades):
    """
    Usa a API gratuita da Groq (Llama 3.3) para gerar uma segunda opinião clínica.
    Modelo atualizado para evitar erro de 'decommissioned'.
    """
    # Tenta pegar a chave dos segredos do Streamlit ou variáveis de ambiente
    api_key = os.environ.get("GROQ_API_KEY") 
    
    if not api_key:
        return "⚠️ Erro: API Key da Groq não encontrada. Configure na barra lateral."

    client = Groq(api_key=api_key)

    system_prompt = """
    Você é um Oncologista Sênior e Farmacêutico Clínico. 
    Analise o caso focando em: 1. Validação da gravidade; 2. Manejo de sintomas; 3. Segurança da Cisplatina.
    Responda em Português (Brasil). Seja conciso, técnico e use tópicos.
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
            # Modelo atualizado e estável (Dez 2025)
            model="llama-3.3-70b-versatile", 
            temperature=0.2,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro na conexão com Groq: {str(e)}"