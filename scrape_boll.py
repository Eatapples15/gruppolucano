import requests
from bs4 import BeautifulSoup
import json
import datetime

def scrape_campania():
    # URL: https://bollettinimeteo.regione.campania.it/?cat=3
    # Logica: Cerca l'ultimo bollettino e estrae i colori delle zone (Zona 1, Zona 2, ecc.)
    url = "https://bollettinimeteo.regione.campania.it/?cat=3"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Esempio semplificato: cerchiamo la tabella delle criticità
        # Nota: Qui andrebbe raffinato il selettore CSS in base alla struttura esatta
        campania_data = {"Salerno": "VERDE"} # Valore default
        # ... logica di parsing ...
        return campania_data
    except Exception as e:
        print(f"Errore Campania: {e}")
        return {}

def scrape_calabria():
    # URL: https://www.protezionecivilecalabria.it/
    url = "https://www.protezionecivilecalabria.it/"
    try:
        response = requests.get(url)
        # La Calabria spesso usa un'immagine o un PDF; lo scraping avanzato 
        # potrebbe richiedere l'analisi del testo o di API interne se presenti.
        calabria_data = {"Cosenza": "VERDE"}
        return calabria_data
    except Exception as e:
        print(f"Errore Calabria: {e}")
        return {}

def main():
    # 1. Recupera Basilicata (dal tuo JSON esistente)
    res_bas = requests.get("https://raw.githubusercontent.com/Eatapples15/allerte_bollettino_basilicata/refs/heads/main/dati_bollettino.json")
    dati_finali = res_bas.json() if res_bas.status_code == 200 else {}

    # 2. Integra Campania e Calabria
    dati_finali.update(scrape_campania())
    dati_finali.update(scrape_calabria())

    # 3. Aggiungi timestamp
    output = {
        "metadata": {
            "last_update": datetime.datetime.now().isoformat(),
            "status": "success"
        },
        "alerts": dati_finali
    }

    # 4. Salva il file
    with open('tutto_bollettino.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()
