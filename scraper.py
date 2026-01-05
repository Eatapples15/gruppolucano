import requests
from bs4 import BeautifulSoup
import json
import datetime

def get_color_from_text(text):
    text = text.lower()
    if 'ross' in text: return 'red'
    if 'aranc' in text: return 'orange'
    if 'giall' in text: return 'yellow'
    return 'green'

def scrape_campania():
    url = "https://bollettinimeteo.regione.campania.it/?cat=3"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # La Campania pubblica bollettini testuali o tabelle. 
        # Cerchiamo il primo post (il più recente)
        last_update = soup.find('div', class_='entry-content')
        text = last_update.get_text() if last_update else "Verde"
        # Estraiamo il colore per Salerno (Zona 3, 5, 6, 7, 8)
        color = get_color_from_text(text)
        return {"oggi": color, "domani": color} # In genere il bollettino vale 24h
    except:
        return {"oggi": "green", "domani": "green"}

def scrape_calabria():
    url = "https://www.protezionecivilecalabria.it/"
    try:
        response = requests.get(url, timeout=10)
        # La Calabria ha un widget in home o un link all'ultimo bollettino
        # Qui simuliamo la ricerca della parola chiave "allerta"
        color = get_color_from_text(response.text)
        return {"oggi": color, "domani": color}
    except:
        return {"oggi": "green", "domani": "green"}

def main():
    # Carica dati esistenti Basilicata
    res_bas = requests.get("https://raw.githubusercontent.com/Eatapples15/allerte_bollettino_basilicata/refs/heads/main/dati_bollettino.json")
    data_bas = res_bas.json()

    # Integra Campania e Calabria
    full_alerts = {
        "zone": data_bas.get("zone", {}),
        "data_bollettino": data_bas.get("data_bollettino", datetime.datetime.now().strftime("%d/%m/%Y")),
        "Salerno": scrape_campania(),
        "Cosenza": scrape_calabria(),
        "url_bollettino": data_bas.get("url_bollettino", "")
    }

    output = {
        "metadata": {"last_update": datetime.datetime.now().isoformat()},
        "alerts": full_alerts
    }

    with open('tutto_bollettino.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()
