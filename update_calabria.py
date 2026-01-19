import requests
import json
from datetime import datetime

API_URL = "https://pc2.protezionecivilecalabria.it/api/alerts/last-mau"
JSON_FILE = "calabria.json"
ZONE_COSENZA = [1, 2, 5, 6]

def get_color_norm(val):
    if val is None: return "unknown"
    v = str(val).upper()
    # Supporto per codici numerici (1=verde, 2=giallo, 3=arancione, 4=rosso)
    if v == "1" or "VERD" in v: return "verde"
    if v == "2" or "GIALL" in v: return "gialla"
    if v == "3" or "ARANC" in v: return "arancione"
    if v == "4" or "ROSS" in v: return "rossa"
    return "unknown"

try:
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    data = r.json()

    output_zones = {}
    for z_id in ZONE_COSENZA:
        output_zones[str(z_id)] = {"oggi": "unknown", "domani": "unknown"}

    debug_sample = None

    def process_period(period_key, day_label):
        global debug_sample
        items = data.get(period_key, [])
        if not isinstance(items, list): return
        
        for item in items:
            if not debug_sample: debug_sample = item # Salviamo un campione per debug
            
            # Ricerca ID Zona in tutte le chiavi possibili
            zid_raw = item.get('id_zona') or item.get('id_area') or item.get('id') or item.get('zona')
            zid = str(zid_raw) if zid_raw else ""
            
            if zid.isdigit() and int(zid) in ZONE_COSENZA:
                # Ricerca Livello in tutte le chiavi possibili
                level = item.get('id_livello') or item.get('livello') or item.get('colore') or item.get('allerta')
                output_zones[zid][day_label] = get_color_norm(level)

    process_period('today', 'oggi')
    process_period('tomorrow', 'domani')

    final_json = {
        "zone_calabria": output_zones,
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Validazione completata",
        "debug_item_sample": debug_sample # Questo ci dirà l'esatta struttura se fallisce ancora
    }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, indent=2)

except Exception as e:
    with open(JSON_FILE, 'w') as f:
        json.dump({"status": f"Errore: {str(e)}", "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M")}, f)
