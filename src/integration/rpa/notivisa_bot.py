from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import webbrowser

NOTIVISA_URL = "https://notivisa.anvisa.gov.br/frmLogin.asp"

class NotivisaAutomator:
    def open_portal(self):
        # CORRECAO: Removido emoji para evitar erro de encoding no Windows
        print(f"[INFO] Abrindo Notivisa: {NOTIVISA_URL}")
        webbrowser.open(NOTIVISA_URL)
        return {"status": "opened", "msg": "Portal aberto."}

    def generate_copy_paste_report(self, incident_data):
        return f"""
        === DADOS PARA NOTIVISA ===
        PACIENTE ID: {incident_data.get('patient_id')}
        EVENTO: {incident_data.get('event')}
        GRAU (CTCAE): {incident_data.get('grade')}
        DATA: {incident_data.get('date')}
        DESCRIÇÃO: {incident_data.get('notes')}
        ===========================
        """
