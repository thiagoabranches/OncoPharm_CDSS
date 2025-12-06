from adapters.hl7_tasy_mv import HospitalInterfaceEngine
import time
import random

def run_simulation():
    engine = HospitalInterfaceEngine()
    
    print("🏥 --- SIMULADOR DE INTERFACEAMENTO HOSPITALAR (HL7) ---")
    print("Simulando envio de exames pelo Tasy...")
    print("(Pressione CTRL+C para parar)")
    
    # Lista de pacientes simulados
    pacientes = ["1001", "1002", "1003"]
    
    # Mensagem Template (Formato padrão HL7 pipe-delimited)
    # PID|...|ID_PACIENTE...
    # OBX|...|NOME_EXAME||VALOR|UNIDADE...
    hl7_template = "MSH|^~\&|TASY|LAB|ONCO|CDSS|20251206||ORU^R01|MSG{msg_id}|P|2.3\rPID|1||{pid}||PACIENTE^SIMULADO\rOBR|1|||{exam_code}^{exam_name}\rOBX|1|NM|{exam_code}||{val}|{unit}|||{flag}||F"

    while True:
        # Gerar dados aleatórios
        pid = random.choice(pacientes)
        creatinina = round(random.uniform(0.8, 3.5), 2) # Valores normais e tóxicos
        flag = "H" if creatinina > 1.5 else "N" # H = High (Alto)
        msg_id = random.randint(1000, 9999)
        
        # Montar mensagem
        hl7_msg = hl7_template.format(
            msg_id=msg_id, pid=pid, 
            exam_code="CREAT", exam_name="Creatinina Serica",
            val=creatinina, unit="mg/dL", flag=flag
        )
        
        # Enviar para o motor de integração
        print(f"\n📡 [Tasy] Enviando exame MSG-{msg_id}...")
        engine.parse_oru_message(hl7_msg)
        
        print("⏳ Aguardando próximo exame...")
        time.sleep(5) # Envia um novo a cada 5 segundos

if __name__ == "__main__":
    run_simulation()
