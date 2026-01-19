import requests
import json
import os
from datetime import datetime

# Configurazione
API_URL = "https://pc2.protezionecivilecalabria.it/api/alerts/last-mau"
JSON_FILE = "calabria.json"
ZONE_COSENZA = [1, 2, 5, 6]

def get_alert_level(level_id):
    # Converte i codici numerici o testuali dell'API in colori validi per la tua dashboard
    mapping = {
        1: "verde", 2: "gialla", 3: "arancione", 4: "rossa",
        "VERDE": "verde", "GIALLO": "gialla", "ARANCIONE": "arancione", "ROSSO": "rossa"
    }
    return mapping.get(level_id, "unknown")

try:
    response = requests.get(API_URL, timeout=20)
    response.raise_for_status()
    data = response.json()

    new_data = {
        "zone_calabria": {},
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    # Estrazione dati per le zone di Cosenza
    # Nota: La struttura dipende dall'output esatto dell'API (zones o alert_today)
    zones = data.get('zones', [])
    for zone in zones:
        z_id = int(zone.get('id', 0))
        if z_id in ZONE_COSENZA:
            new_data["zone_calabria"][str(z_id)] = {
                "oggi": get_alert_level(zone.get('alert_level_today')),
                "domani": get_alert_level(zone.get('alert_level_tomorrow'))
            }

    # Salvataggio su file
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2)
    
    print("Aggiornamento completato con successo.")

except Exception as e:
    print(f"Errore durante l'aggiornamento: {e}")
