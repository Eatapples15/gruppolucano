import requests
import json
from datetime import datetime

# Sorgente ufficiale Calabria
API_URL = "https://pc2.protezionecivilecalabria.it/api/alerts/last-mau"
JSON_FILE = "calabria.json"
ZONE_COSENZA = [1, 2, 5, 6]

def get_color_norm(val):
    if not val: return "unknown"
    val = str(val).upper()
    if any(x in val for x in ["ROSS", "4"]): return "rossa"
    if any(x in val for x in ["ARANC", "3"]): return "arancione"
    if any(x in val for x in ["GIALL", "2"]): return "gialla"
    if any(x in val for x in ["VERD", "1"]): return "verde"
    return "unknown"

def find_zones(obj):
    """Cerca ricorsivamente le zone nel JSON dell'API"""
    zones_found = []
    if isinstance(obj, list):
        for item in obj:
            zones_found.extend(find_zones(item))
    elif isinstance(obj, dict):
        # Se l'oggetto ha un ID che somiglia a una zona
        z_id = obj.get('id') or obj.get('numero') or obj.get('id_zona')
        if z_id and str(z_id).isdigit() and int(z_id) in ZONE_COSENZA:
            zones_found.append(obj)
        else:
            for v in obj.values():
                zones_found.extend(find_zones(v))
    return zones_found

try:
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    raw_data = r.json()

    extracted_zones = find_zones(raw_data)
    
    final_output = {
        "zone_calabria": {},
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Dati validati" if extracted_zones else "ERRORE: Struttura API non riconosciuta"
    }

    for z in extracted_zones:
        zid = str(z.get('id') or z.get('numero') or z.get('id_zona'))
        # Cerca i livelli di allerta
        oggi = z.get('alert_level_today') or z.get('today', {}).get('level') or z.get('criticità_oggi')
        domani = z.get('alert_level_tomorrow') or z.get('tomorrow', {}).get('level') or z.get('criticità_domani')
        
        final_output["zone_calabria"][zid] = {
            "oggi": get_color_norm(oggi),
            "domani": get_color_norm(domani)
        }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2)
    print("Aggiornamento completato.")

except Exception as e:
    print(f"Errore: {e}")
