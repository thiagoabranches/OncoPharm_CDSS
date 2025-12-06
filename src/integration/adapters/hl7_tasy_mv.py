import hl7
import sqlite3
import datetime
import os

# Caminho do banco
DB_PATH = "database/oncopharm.db"

class HospitalInterfaceEngine:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def parse_oru_message(self, hl7_string):
        """
        Traduz mensagens HL7 (Tipo ORU^R01 - Resultado de Exame)
        usadas por Tasy, MV, SoulMV, etc.
        """
        try:
            h = hl7.parse(hl7_string)
            
            # 1. Extração de Dados (Navegando nos segmentos HL7)
            # MSH: Cabeçalho | PID: Paciente | OBR: Pedido | OBX: Resultado
            
            # PID|1|12345... (O ID do paciente costuma estar no índice 3)
            # Nota: O uso de str() garante compatibilidade
            pid_segment = h.segment('PID')
            patient_id_ext = str(pid_segment[3]) 
            
            # OBX|1|NM|CREAT^Creatinina||1.5|mg/dL... 
            # (Nome no índice 3, Resultado no 5, Unidade no 6)
            obx_segment = h.segment('OBX')
            exame_nome = str(obx_segment[3])
            resultado_valor = str(obx_segment[5])
            unidade = str(obx_segment[6])
            
            print(f"🔄 [HL7] Recebido do Tasy: Paciente {patient_id_ext} | {exame_nome}: {resultado_valor} {unidade}")
            
            # 2. Persistir no OMOP (SQL)
            self._save_to_sql(patient_id_ext, exame_nome, resultado_valor, unidade)
            return {"status": "success", "patient": patient_id_ext, "result": resultado_valor}

        except Exception as e:
            print(f"❌ Erro ao processar HL7: {e}")
            return {"status": "error", "msg": str(e)}

    def _save_to_sql(self, patient_id, concept, value, unit):
        """Insere o dado externo na tabela 'episode' do nosso banco."""
        if not os.path.exists(self.db_path):
            print("❌ Erro: Banco de dados não encontrado.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Descrição amigável para o farmacêutico ver no dashboard
        source_desc = f"Integração Tasy: {concept} = {value} {unit}"
        
        # Inserção
        sql = """
        INSERT INTO episode (
            person_id, episode_concept_id, episode_start_date, 
            episode_number, episode_source_value, 
            episode_object_concept_id, episode_type_concept_id
        ) VALUES (?, 32531, ?, 99, ?, 0, 0);
        """
        # episode_number 99 = Código interno para "Dado Integrado"
        
        try:
            cursor.execute(sql, (patient_id, datetime.date.today(), source_desc))
            conn.commit()
            print("💾 Dado integrado salvo no Prontuário SQL.")
        except Exception as e:
            print(f"⚠️ Erro de banco: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    # Teste rápido: Simulando uma mensagem real do Tasy
    msg_teste = "MSH|^~\&|TASY|LAB|ONCO|CDSS|20251206||ORU^R01|123|P|2.3\rPID|1||99999^^^TASY||TESTE^INTEGRACAO\rOBR|1|||HEMOG^Hemoglobina\rOBX|1|NM|HEMOG||9.5|g/dL|||L||F"
    engine = HospitalInterfaceEngine()
    engine.parse_oru_message(msg_teste)
