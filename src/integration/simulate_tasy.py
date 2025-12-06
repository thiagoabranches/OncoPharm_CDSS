from adapters.hl7_tasy_mv import HospitalInterfaceEngine
import time
import random

def run_simulation():
    engine = HospitalInterfaceEngine()
    
    # Versao Estavel: Simulador Generico (Sem Emojis)
    print("[INFO] SIMULADOR TASY/MV INICIADO (MODO GENERICO)")
    print("Enviando exames de rotina...")
    
    pacientes = ["1001", "1002", "1003"]
    
    # Template HL7 Padrao
    hl7_template = "MSH|^~\&|TASY|LAB|ONCO|CDSS|20251206||ORU^R01|MSG{msg_id}|P|2.3\rPID|1||{pid}||PACIENTE^SIMULADO\rOBR|1|||{exam_code}^{exam_name}\rOBX|1|NM|{exam_code}||{val}|{unit}|||{flag}||F"

    while True:
        pid = random.choice(pacientes)
        # Gera Creatinina (Foco em Toxicidade Renal - Funcionalidade Principal)
        creatinina = round(random.uniform(0.8, 3.5), 2)
        flag = "H" if creatinina > 1.5 else "N"
        msg_id = random.randint(1000, 9999)
        
        hl7_msg = hl7_template.format(
            msg_id=msg_id, pid=pid, 
            exam_code="CREAT", exam_name="Creatinina Serica",
            val=creatinina, unit="mg/dL", flag=flag
        )
        
        print(f"\n[Tasy] Enviando exame MSG-{msg_id} para Paciente {pid} (Valor: {creatinina})")
        engine.parse_oru_message(hl7_msg)
        
        time.sleep(5)

if __name__ == "__main__":
    run_simulation()
