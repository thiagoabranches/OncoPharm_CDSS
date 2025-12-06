import re

class PharmacovigilanceNLP:
    def __init__(self):
        # Dicionário simplificado de termos CTCAE (Toxicidade)
        # Na prática, isso seria um modelo LLM ou ontologia médica
        self.tox_terms = {
            "neutropenia": {"grau": "G3/G4", "risco": "Alto", "acao": "Monitorar Febre"},
            "febre":       {"grau": "G1/G2", "risco": "Médio", "acao": "Investigar Infecção"},
            "rash":        {"grau": "G1/G2", "risco": "Baixo", "acao": "Avaliar Anti-histamínico"},
            "diarreia":    {"grau": "G2",    "risco": "Médio", "acao": "Hidratação"},
            "neuropatia":  {"grau": "G1",    "risco": "Baixo", "acao": "Monitorar Dose Acumulada"},
            "sangramento": {"grau": "G3",    "risco": "Alto",  "acao": "URGENTE: Coagulograma"}
        }

    def analyze_text(self, text):
        """
        Analisa texto livre buscando menções a eventos adversos (AEs).
        Retorna uma lista de alertas estruturados.
        """
        if not text:
            return []
            
        text_lower = text.lower()
        detected_events = []
        
        for term, info in self.tox_terms.items():
            # Busca regex simples (palavra inteira)
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                detected_events.append({
                    "termo": term.capitalize(),
                    "grau_provavel": info['grau'],
                    "risco": info['risco'],
                    "sugestao": info['acao']
                })
                
        return detected_events

# Teste rápido
if __name__ == "__main__":
    nlp = PharmacovigilanceNLP()
    texto = "Paciente refere febre noturna e leve rash nos braços."
    print(nlp.analyze_text(texto))
