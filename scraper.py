import json
import requests
import datetime

def get_data():
    # Simulazione scraping Campania e Calabria
    # Qui dovresti inserire la tua logica BeautifulSoup
    alerts = {
        "zone": {
            "BASI A1": {"oggi": "green", "domani": "yellow"},
            "BASI A2": {"oggi": "green", "domani": "yellow"},
            "BASI B": {"oggi": "green", "domani": "yellow"},
            "BASI C": {"oggi": "green", "domani": "yellow"},
            "BASI D": {"oggi": "green", "domani": "yellow"},
            "BASI E1": {"oggi": "green", "domani": "yellow"},
            "BASI E2": {"oggi": "green", "domani": "yellow"}
        },
        "data_bollettino": datetime.datetime.now().strftime("%d/%m/%Y"),
        "Salerno": {
            "oggi": "green", 
            "domani": "yellow"  # Integrato come richiesto
        },
        "Cosenza": {
            "oggi": "green", 
            "domani": "green"   # Integrato come richiesto
        },
        "url_bollettino": "https://..."
    }
    
    output = {
        "metadata": {"last_update": datetime.datetime.now().isoformat()},
        "alerts": alerts
    }
    
    with open('tutto_bollettino.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    get_data()
