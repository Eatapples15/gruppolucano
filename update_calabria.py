import requests
import json
import os
from datetime import datetime

# URL API Ufficiale Calabria
API_URL = "https://pc2.protezionecivilecalabria.it/api/alerts/last-mau"
JSON_FILE = "calabria.json"
ZONE_COSENZA = [1, 2, 5, 6]

def get_color(val):
    if not val: return "unknown"
    val = str(val).upper()
    if "ROSS" in val or "4" in val: return "rossa"
    if "ARANC" in val or "3" in val: return "arancione"
    if "GIALL" in val or "2" in val: return "gialla"
    if "VERD" in val or "1" in val: return "verde"
    return "unknown"

def sync():
    try:
        print(f"Tentativo di connessione a {API_URL}...")
        r = requests.get(API_URL, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # Debug: stampa le chiavi principali per capire la struttura
        print(f"Chiavi trovate nell'API: {list(data.keys())}")

        new_data = {
            "zone_calabria": {},
            "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "status": "Dati aggiornati correttamente"
        }

        # Cerchiamo i dati nelle strutture comuni (zones, data, o root)
        zones_source = data.get('zones') or data.get('data', {}).get('zones') or []
        
        if not zones_source and isinstance(data, list):
            zones_source = data

        for z in zones_source:
            # L'ID può essere sotto 'id', 'id_zona' o 'numero'
            z_id = z.get('id') or z.get('id_zona') or z.get('numero')
            if z_id and int(z_id) in ZONE_COSENZA:
                # Estraiamo il livello massimo tra oggi e domani
                # Nota: le chiavi variano spesso tra 'alert_level_today' o 'today' -> 'level'
                oggi_raw = z.get('alert_level_today') or z.get('today', {}).get('level')
                domani_raw = z.get('alert_level_tomorrow') or z.get('tomorrow', {}).get('level')
                
                new_data["zone_calabria"][str(z_id)] = {
                    "oggi": get_color(oggi_raw),
                    "domani": get_color(domani_raw)
                }

        # Se non abbiamo trovato nulla, scriviamo un errore nel JSON per diagnosi
        if not new_data["zone_calabria"]:
            new_data["status"] = "ERRORE: Nessuna zona di Cosenza trovata nel flusso API"
            print("Attenzione: Nessuna zona trovata.")

        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2)
            
        print(f"File {JSON_FILE} salvato con successo.")

    except Exception as e:
        error_msg = f"Errore critico: {str(e)}"
        print(error_msg)
        # Salviamo comunque il timestamp per sapere che il bot è vivo
        with open(JSON_FILE, 'w') as f:
            json.dump({"status": error_msg, "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M")}, f)

if __name__ == "__main__":
    sync()
