from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import datetime

app = FastAPI(title="OncoPharm Integration Hub", version="1.0")

# Modelo de Dados (JSON esperado)
class LabResult(BaseModel):
    patient_id: int
    exam_code: str
    value: float
    unit: str
    source_system: str  # Ex: "SAP", "Totvs", "AppTriagem"

DB_PATH = "database/oncopharm.db"

@app.post("/api/v1/integrate/lab-result")
async def receive_lab_result(data: LabResult):
    """
    Endpoint genérico para receber exames de qualquer sistema externo.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Formata para o padrão OMOP da nossa tabela episode
        source_desc = f"API ({data.source_system}): {data.exam_code} = {data.value} {data.unit}"
        
        sql = """
        INSERT INTO episode (
            person_id, episode_concept_id, episode_start_date, 
            episode_number, episode_source_value, 
            episode_object_concept_id, episode_type_concept_id
        ) VALUES (?, 32531, ?, 99, ?, 0, 0);
        """
        
        cursor.execute(sql, (data.patient_id, datetime.date.today(), source_desc))
        conn.commit()
        conn.close()
        
        return {"status": "received", "details": f"Dados de {data.source_system} integrados."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "online", "system": "OncoPharm Integration Module"}

# Instrução para rodar: uvicorn src.integration.api_server:app --reload
