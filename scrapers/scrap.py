import base64
import os
import random
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import re
import json

from requests.adapters import HTTPAdapter
from urllib3 import Retry

MAIN_URL = 'https://fbref.com'
URL_COMPS = f'{MAIN_URL}/en/comps/'

def load_progress(filename="progress2.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Progress loaded from {filename}")
        return data
    return {}

def save_progress(data, filename="progress2.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Progress saved to {filename}")

# Funkcja wykonująca request z opóźnieniem
def safe_request(url, min_delay=6, max_delay=8, retries=3):
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # delay = random.uniform(min_delay, max_delay)
    time.sleep(min_delay)
    return response

# Scraper lig i ich linków
def scrape_leagues(data, comps_url):
    try:
        response = safe_request(comps_url)
        if response.status_code != 200:
            print(f"Błąd przy pobieraniu danych z {comps_url}, kod: {response.status_code}")
            response = safe_request(comps_url)
            if response.status_code != 200:
                print(f"Błąd przy pobieraniu danych z {comps_url}, kod: {response.status_code}")
                return {}

        soup = bs(response.text, 'html.parser')
        table = soup.find('table', {'id': 'comps_club'})
        rows = table.find_all('tr')
        leagues = {}

        for row in rows[1:len(rows) - 1]:
            league_name = ''
            league_link = ''
            links = row.find_all('a')
            for link in links:
                if 'history' in link['href']:
                    league_name = link.text
                if f'{datetime.now().year}' in link.text:
                    league_link = link['href']
                    break
            leagues[league_name] = {'link': league_link}
        data['leagues'] = leagues
    except Exception as e:
        print(f"Error in scrape_leagues: {e}")
        save_progress(data)

def scrape_teams(data, main_url):
    try:
        for league in data['leagues'].keys():
            print(f"Pobieram drużyny z ligi: {league}...")
            teams = {}
            response = safe_request(f"{main_url}{data['leagues'][league]['link']}")
            if response.status_code != 200:
                print(f"Błąd przy pobieraniu drużyn z ligi {league}, kod: {response.status_code}")
                continue

            soup = bs(response.content, 'html.parser')
            league_img_tag = soup.find('img', {'class': 'teamlogo'})
            if league_img_tag and 'src' in league_img_tag.attrs:
                league_img = league_img_tag['src']
                response = safe_request(league_img)
                if response.status_code == 200:
                    encoded_image = base64.b64encode(response.content).decode('utf-8')
                    data['leagues'][league]['img'] = encoded_image
                else:
                    print(f"Błąd przy pobieraniu zdjęcia ligi {league}, kod: {response.status_code}")
            else:
                print(f"Brak zdjęcia dla ligi {league}")

            table = soup.find('table', {'id': re.compile(r'overall$')})
            if not table:
                print(f"Nie znaleziono tabeli z drużynami dla ligi {league}")
                continue

            rows = table.find_all('tr')
            for row in rows[1:]:
                if not row.a:
                    continue
                team_name = row.a.text.strip()
                team_link = row.a['href']
                teams[team_name] = {'link': team_link}

            data['leagues'][league]['teams'] = teams
    except Exception as e:
        print(f"Error in scrape_teams: {e}")
        save_progress(data)


def scrape_players(data, main_url):
    try:
        for league in data['leagues'].keys():
            for team in data['leagues'][league]['teams'].keys():
                print(f"Pobieram zawodników z drużyny: {team} ({league})...")
                players = {}
                response = safe_request(f"{main_url}{data['leagues'][league]['teams'][team]['link']}")
                if response.status_code != 200:
                    print(f"Błąd przy pobieraniu zawodników dla drużyny {team}, kod: {response.status_code}")
                    continue

                soup = bs(response.content, 'html.parser')
                team_img_tag = soup.find('img', {'class': 'teamlogo'})
                if team_img_tag and 'src' in team_img_tag.attrs:
                    team_img = team_img_tag['src']
                    response = safe_request(team_img)
                    if response.status_code == 200:
                        encoded_image = base64.b64encode(response.content).decode('utf-8')
                        data['leagues'][league]['teams'][team]['img'] = encoded_image
                    else:
                        print(f"Błąd przy pobieraniu zdjęcia klubu {team}, kod: {response.status_code}")
                else:
                    print(f"Brak zdjęcia dla klubu {team}")

                table = soup.find('table', {'id': re.compile(r'^stats')})
                if not table:
                    print(f"Nie znaleziono tabeli z zawodnikami dla drużyny {team}")
                    continue

                rows = table.find_all('tr')
                for row in rows[2:-2]:
                    if not row.a:
                        continue
                    player_name = row.a.text.strip()
                    position_cell = row.find('td', {'data-stat': 'position'})
                    player_position = position_cell.text.strip() if position_cell else "N/A"
                    player_link = row.a['href']
                    players[player_name] = {'position': player_position, 'link': player_link}

                data['leagues'][league]['teams'][team]['players'] = players
    except Exception as e:
        print(f"Error in scrape_players: {e}")
        save_progress(data)

def scrape_players_info(data, main_url):
    try:
        for league in data['leagues'].keys():
            for team in data['leagues'][league]['teams'].keys():
                for player in data['leagues'][league]['teams'][team]['players'].keys():
                    if data['leagues'][league]['teams'][team]['players'][player]['link'] == '':
                        continue
                    if 'img' not in data['leagues'][league]['teams'][team]['players'][player]:
                        print(f"Pobieram informacje o zawodniku: {player} ({team}, {league})...")
                        response = safe_request(f"{main_url}{data['leagues'][league]['teams'][team]['players'][player]['link']}")
                        if response.status_code != 200:
                            print(f"Błąd przy pobieraniu informacji o zawodniku {player}, kod: {response.status_code}")
                            continue

                        soup = bs(response.content, 'html.parser')
                        player_img_tag = soup.find('img', {'alt': re.compile(r'headshot$')})
                        if player_img_tag and ('src' in player_img_tag.attrs):
                            player_img = player_img_tag['src']
                            response = safe_request(player_img)
                            if response.status_code == 200:
                                encoded_image = base64.b64encode(response.content).decode('utf-8')
                                data['leagues'][league]['teams'][team]['players'][player]['img'] = encoded_image
                            else:
                                print(f"Błąd przy pobieraniu zdjęcia zawodnika {player}, kod: {response.status_code}")
                        else:
                            print(f"Brak zdjęcia dla zawodnika {player}")
                            #set img to '' if no image found
                            data['leagues'][league]['teams'][team]['players'][player]['img'] = ''
    except Exception as e:
        print(f"Error in scrape_players_info: {e}")
        save_progress(data)

if __name__ == "__main__":
    data = load_progress()

    # Pobierz ligi
    # scrape_leagues(data, URL_COMPS)

    # Pobierz drużyny z lig
    # scrape_teams(data, MAIN_URL)

    # Pobierz zawodników z drużyn
    # scrape_players(data, MAIN_URL)

    # Pobierz informacje o zawodnikach
    scrape_players_info(data, MAIN_URL)

    # Zapisz wyniki do pliku JSON
    with open("data/fbref_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Zakończono scrapowanie i zapisano dane do fbref_data.json")
