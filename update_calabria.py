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

def find_data_recursive(obj):
    """Cerca zone e colori in profondità nel JSON"""
    extracted = {}
    
    if isinstance(obj, list):
        for item in obj:
            extracted.update(find_data_recursive(item))
    elif isinstance(obj, dict):
        # Proviamo a vedere se questo oggetto è una zona
        # Cerchiamo ID o Numero della zona
        z_id = obj.get('id') or obj.get('numero') or obj.get('id_zona') or obj.get('zona')
        
        if z_id and str(z_id).isdigit() and int(z_id) in ZONE_COSENZA:
            # Abbiamo trovato una zona di interesse, cerchiamo l'allerta
            # Cerchiamo chiavi comuni per oggi e domani
            oggi = obj.get('alert_level_today') or obj.get('today', {}).get('level') or obj.get('stato_oggi') or obj.get('criticita_idro_oggi')
            domani = obj.get('alert_level_tomorrow') or obj.get('tomorrow', {}).get('level') or obj.get('stato_domani') or obj.get('criticita_idro_domani')
            
            extracted[str(z_id)] = {
                "oggi": get_color_norm(oggi),
                "domani": get_color_norm(domani)
            }
        else:
            # Se non è una zona, scava più a fondo nei valori
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    extracted.update(find_data_recursive(v))
    return extracted

try:
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    raw_data = r.json()

    # Avvia la scansione profonda
    results = find_data_recursive(raw_data)
    
    output = {
        "zone_calabria": results,
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Dati validati" if results else "ERRORE: Zone non trovate nel flusso JSON",
        "debug_raw_keys": list(raw_data.keys()) if isinstance(raw_data, dict) else "list_root"
    }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"Update completato. Zone trovate: {list(results.keys())}")

except Exception as e:
    error_data = {
        "zone_calabria": {},
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": f"Errore critico: {str(e)}"
    }
    with open(JSON_FILE, 'w') as f:
        json.dump(error_data, f)
