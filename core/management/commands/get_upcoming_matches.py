import cloudscraper
import requests
from django.core.management.base import BaseCommand
from core.models import UpcomingMatch, Team
from datetime import datetime
from bs4 import BeautifulSoup as bs

class Command(BaseCommand):
    help = 'Scrap upcoming matches directly to the database'

    def handle(self, *args, **kwargs):
        main_url = 'https://fbref.com'
        url_comps = f'{main_url}/en/comps/'

        scraper = cloudscraper.create_scraper()
        try:
            response = scraper.get(url_comps)
            response.raise_for_status()
        except cloudscraper.exceptions.CloudflareChallengeError as e:
            self.stdout.write(self.style.ERROR(f'Error fetching URL {url_comps}: {e}'))
            return

        try:
            soup = bs(response.text, 'html.parser')
            table = soup.find('table', {'id': 'comps_club'})
            if table is None:
                raise ValueError('Could not find the table with id "comps_club"')
            rows = table.find_all('tr')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error parsing HTML: {e}'))
            return

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

        for league in leagues.keys():
            try:
                league_link = leagues[league]['link']
                league_link = league_link.split('/')
                league_link = f'{main_url}/en/comps/{league_link[3]}/schedule/{league_link[4]}-Scores-and-Fixtures'
                leagues[league]['link'] = league_link
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing league link for {league}: {e}'))
                continue

        for league in leagues.keys():
            league_link = leagues[league]['link']
            try:
                response = requests.get(league_link)
                response.raise_for_status()
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Error fetching URL {league_link}: {e}'))
                continue

            try:
                soup = bs(response.content, 'html.parser')
                table = soup.find('table')
                if table is None:
                    raise ValueError(f'Could not find the table for league {league}')
                rows = table.find_all('tr')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error parsing HTML for league {league}: {e}'))
                continue

            for row in rows:
                if row.has_attr('style'):
                    continue
                try:
                    if (scr := row.find('td', {'data-stat': 'score'})) is not None:
                        if scr.a is None:
                            game_week = row.find('th', {'data-stat': 'gameweek'}).text
                            date = row.find('td', {'data-stat': 'date'}).a.text
                            date = datetime.strptime(date, '%Y-%m-%d').date()
                            home_team = row.find('td', {'data-stat': 'home_team'}).a.text
                            away_team = row.find('td', {'data-stat': 'away_team'}).a.text
                            league_link = leagues[league]['link']
                            UpcomingMatch.objects.get_or_create(
                                game_week=game_week,
                                date=date,
                                home_team=Team.objects.get(name=home_team),
                                away_team=Team.objects.get(name=away_team),
                                league=Team.objects.get(name=home_team).league,
                                league_link=league_link
                            )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing match data: {e}'))
                    continue