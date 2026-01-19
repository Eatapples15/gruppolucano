import requests
import json
from datetime import datetime

API_URL = "https://pc2.protezionecivilecalabria.it/api/alerts/last-mau"
JSON_FILE = "calabria.json"
ZONE_COSENZA = [1, 2, 5, 6]

def get_color_norm(val):
    if val is None: return "unknown"
    v = str(val).upper()
    if v == "1" or "VERD" in v: return "verde"
    if v == "2" or "GIALL" in v: return "gialla"
    if v == "3" or "ARANC" in v: return "arancione"
    if v == "4" or "ROSS" in v: return "rossa"
    return "unknown"

try:
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    data = r.json()

    output_zones = {str(z): {"oggi": "unknown", "domani": "unknown"} for z in ZONE_COSENZA}
    structure_info = {}

    def parse_period(period_key, day_label):
        content = data.get(period_key)
        structure_info[f"{period_key}_type"] = str(type(content))
        
        items = []
        if isinstance(content, list):
            items = content
        elif isinstance(content, dict):
            # Se è un dizionario, proviamo a prendere i valori o cerchiamo una lista interna
            items = list(content.values()) if not any(isinstance(v, dict) for v in content.values()) else [content]
        
        found_in_period = 0
        sample = None
        
        for item in items:
            if isinstance(item, dict):
                if sample is None: sample = item
                # Cerchiamo l'ID zona in varie chiavi possibili
                zid_raw = item.get('id_zona') or item.get('id_area') or item.get('zona_id') or item.get('id')
                zid = str(zid_raw) if zid_raw else ""
                
                if zid.isdigit() and int(zid) in ZONE_COSENZA:
                    # Cerchiamo il livello/colore
                    lvl = item.get('id_livello') or item.get('livello') or item.get('id_stato') or item.get('colore')
                    output_zones[zid][day_label] = get_color_norm(lvl)
                    found_in_period += 1
        
        return found_in_period, sample

    found_oggi, sample_oggi = parse_period('today', 'oggi')
    found_domani, sample_domani = parse_period('tomorrow', 'domani')

    final_json = {
        "zone_calabria": output_zones,
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Dati trovati" if (found_oggi + found_domani) > 0 else "ERRORE: Struttura identificata ma zone non trovate",
        "debug": {
            "struttura": structure_info,
            "count_oggi": found_oggi,
            "count_domani": found_domani,
            "campione_oggi": sample_oggi
        }
    }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, indent=2)

except Exception as e:
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump({"status": f"Errore: {str(e)}", "ts": datetime.now().isoformat()}, f)
