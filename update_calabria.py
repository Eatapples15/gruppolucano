import requests
import json
from datetime import datetime

API_URL = "https://pc2.protezionecivilecalabria.it/api/alerts/last-mau"
JSON_FILE = "calabria.json"
ZONE_COSENZA = [1, 2, 5, 6]

# Rango di gravità per calcolare il massimo rischio
RANK = {"unknown": -1, "verde": 0, "gialla": 1, "arancione": 2, "rossa": 3}

def normalize(val):
    if not val: return "unknown"
    val = str(val).upper()
    if "RED" in val or "ROSS" in val: return "rossa"
    if "ORANGE" in val or "ARANC" in val: return "arancione"
    if "YELLOW" in val or "GIALL" in val: return "gialla"
    if "GREEN" in val or "VERD" in val: return "verde"
    return "unknown"

try:
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    data = r.json()

    final_zones = {}

    for period in ['today', 'tomorrow']:
        label = "oggi" if period == 'today' else "domani"
        # Navigazione sicura nella struttura identificata
        source_zones = data.get(period, {}).get('hydrogeologicalCriticality', {}).get('zones', {})
        
        for num in ZONE_COSENZA:
            z_key = f"cala{num}"
            z_id = str(num)
            if z_id not in final_zones: final_zones[z_id] = {}

            # Estrazione dei due livelli di allerta
            z_data = source_zones.get(z_key, {})
            lv1 = normalize(z_data.get('thunderstormAlertLevel'))
            lv2 = normalize(z_data.get('hydraulicAlertLevel'))

            # Selezione del massimo rischio tra i due
            final_zones[z_id][label] = lv1 if RANK[lv1] >= RANK[lv2] else lv2

    output = {
        "zone_calabria": final_zones,
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Dati validati con successo dalla struttura hydrogeologicalCriticality"
    }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print("Sincronizzazione completata.")

except Exception as e:
    print(f"Errore: {e}")
