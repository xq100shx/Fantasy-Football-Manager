import base64
import json
import os
import random
import re
import time
from datetime import datetime

import cloudscraper
import requests
from django.core.management.base import BaseCommand
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from bs4 import BeautifulSoup as bs

class Command(BaseCommand):
    help = 'Scrap initial data about leagues, teams and players'

    def load_progress(self,filename="progress2.json"):
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
    def safe_request(self, url, min_delay=6, max_delay=8, retries=3):
        scraper = cloudscraper.create_scraper()

        for _ in range(retries):
            try:
                response = scraper.get(url)
                response.raise_for_status()
                time.sleep(random.uniform(min_delay, max_delay))
                return response
            except cloudscraper.exceptions.CloudflareChallengeError as e:
                print(f"Request failed: {e}")
                time.sleep(random.uniform(min_delay, max_delay))

        return None

    # Scraper lig i ich linków
    def scrape_leagues(self,data, comps_url):
        try:
            response = self.safe_request(comps_url)
            if response.status_code != 200:
                print(f"Błąd przy pobieraniu danych z {comps_url}, kod: {response.status_code}")
                response = self.safe_request(comps_url)
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
            self.save_progress(data)

    def scrape_teams(self,data, main_url):
        try:
            for league in data['leagues'].keys():
                print(f"Pobieram drużyny z ligi: {league}...")
                teams = {}
                response = self.safe_request(f"{main_url}{data['leagues'][league]['link']}")
                if response.status_code != 200:
                    print(f"Błąd przy pobieraniu drużyn z ligi {league}, kod: {response.status_code}")
                    continue

                soup = bs(response.content, 'html.parser')
                league_img_tag = soup.find('img', {'class': 'teamlogo'})
                if league_img_tag and 'src' in league_img_tag.attrs:
                    league_img = league_img_tag['src']
                    response = self.safe_request(league_img)
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
            self.save_progress(data)

    def scrape_players(self,data, main_url):
        try:
            for league in data['leagues'].keys():
                for team in data['leagues'][league]['teams'].keys():
                    print(f"Pobieram zawodników z drużyny: {team} ({league})...")
                    players = {}
                    response = self.safe_request(f"{main_url}{data['leagues'][league]['teams'][team]['link']}")
                    if response.status_code != 200:
                        print(f"Błąd przy pobieraniu zawodników dla drużyny {team}, kod: {response.status_code}")
                        continue

                    soup = bs(response.content, 'html.parser')
                    team_img_tag = soup.find('img', {'class': 'teamlogo'})
                    if team_img_tag and 'src' in team_img_tag.attrs:
                        team_img = team_img_tag['src']
                        response = self.safe_request(team_img)
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
            self.save_progress(data)

    def scrape_players_info(self,data, main_url):
        try:
            for league in data['leagues'].keys():
                for team in data['leagues'][league]['teams'].keys():
                    for player in data['leagues'][league]['teams'][team]['players'].keys():
                        if data['leagues'][league]['teams'][team]['players'][player]['link'] == '':
                            continue
                        if 'img' not in data['leagues'][league]['teams'][team]['players'][player]:
                            print(f"Pobieram informacje o zawodniku: {player} ({team}, {league})...")
                            response = self.safe_request(
                                f"{main_url}{data['leagues'][league]['teams'][team]['players'][player]['link']}")
                            if response.status_code != 200:
                                print(
                                    f"Błąd przy pobieraniu informacji o zawodniku {player}, kod: {response.status_code}")
                                continue

                            soup = bs(response.content, 'html.parser')
                            player_img_tag = soup.find('img', {'alt': re.compile(r'headshot$')})
                            if player_img_tag and ('src' in player_img_tag.attrs):
                                player_img = player_img_tag['src']
                                response = self.safe_request(player_img)
                                if response.status_code == 200:
                                    encoded_image = base64.b64encode(response.content).decode('utf-8')
                                    data['leagues'][league]['teams'][team]['players'][player]['img'] = encoded_image
                                else:
                                    print(
                                        f"Błąd przy pobieraniu zdjęcia zawodnika {player}, kod: {response.status_code}")
                            else:
                                print(f"Brak zdjęcia dla zawodnika {player}")
                                # set img to '' if no image found
                                data['leagues'][league]['teams'][team]['players'][player]['img'] = ''
        except Exception as e:
            print(f"Error in scrape_players_info: {e}")
            self.save_progress(data)

    def handle(self, *args, **kwargs):
        MAIN_URL = 'https://fbref.com'
        URL_COMPS = f'{MAIN_URL}/en/comps/'

        data = self.load_progress()

        # Pobierz ligi
        self.scrape_leagues(data, URL_COMPS)

        # Pobierz drużyny z lig
        self.scrape_teams(data, MAIN_URL)

        # Pobierz zawodników z drużyn
        self.scrape_players(data, MAIN_URL)

        # Pobierz informacje o zawodnikach
        self.scrape_players_info(data, MAIN_URL)

        # Zapisz wyniki do pliku JSON
        with open("data/fbref_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Zakończono scrapowanie i zapisano dane do fbref_data.json")
