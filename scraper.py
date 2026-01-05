import json
import requests
import datetime

def main():
    # 1. Recupero dati Basilicata
    res_bas = requests.get("https://raw.githubusercontent.com/Eatapples15/allerte_bollettino_basilicata/refs/heads/main/dati_bollettino.json")
    data_bas = res_bas.json()

    # 2. Struttura raffinata per Salerno e Cosenza
    # Lo scraper dovrà estrarre questi valori dai link che hai fornito
    # Esempio basato sui bollettini del 05/01/2026
    salerno_status = {
        "oggi": "green", 
        "domani": "yellow" 
    }
    cosenza_status = {
        "oggi": "green", 
        "domani": "green"
    }

    full_alerts = {
        "zone": data_bas.get("zone", {}),
        "data_bollettino": data_bas.get("data_bollettino", ""),
        "Salerno": salerno_status,
        "Cosenza": cosenza_status,
        "url_bollettino": data_bas.get("url_bollettino", ""),
        "validita_fine": data_bas.get("validita_fine", "")
    }

    output = {
        "metadata": {"last_update": datetime.datetime.now().isoformat()},
        "alerts": full_alerts
    }

    with open('tutto_bollettino.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()
