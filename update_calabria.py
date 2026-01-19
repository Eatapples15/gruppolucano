import requests
import json
from datetime import datetime

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

try:
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    data = r.json()

    # Inizializziamo la struttura di output
    output_zones = {}
    for z_id in ZONE_COSENZA:
        output_zones[str(z_id)] = {"oggi": "unknown", "domani": "unknown"}

    # Funzione per estrarre i dati dalle liste today/tomorrow
    def fill_period(period_key, day_label):
        period_data = data.get(period_key, [])
        # Se è una lista (probabile)
        if isinstance(period_data, list):
            for item in period_data:
                # Cerchiamo l'ID zona (spesso 'id_zona' o 'id')
                zid = str(item.get('id_zona') or item.get('id') or "")
                if zid.isdigit() and int(zid) in ZONE_COSENZA:
                    # Estraiamo il livello (spesso 'id_livello' o 'colore')
                    level = item.get('id_livello') or item.get('colore') or item.get('allerta')
                    output_zones[zid][day_label] = get_color_norm(level)
        # Se è un dizionario (alternativa)
        elif isinstance(period_data, dict):
            for zid, val in period_data.items():
                if zid.isdigit() and int(zid) in ZONE_COSENZA:
                    output_zones[zid][day_label] = get_color_norm(val)

    # Riempiamo oggi e domani
    fill_period('today', 'oggi')
    fill_period('tomorrow', 'domani')

    final_json = {
        "zone_calabria": output_zones,
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Dati validati correttamente"
    }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, indent=2)
    print("Sincronizzazione completata con successo.")

except Exception as e:
    print(f"Errore: {e}")
