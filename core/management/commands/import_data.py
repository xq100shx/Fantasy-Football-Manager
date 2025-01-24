import base64
import json
from django.core.management.base import BaseCommand
from core.models import League, Team, Player

class Command(BaseCommand):
    help = 'Import football data from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Ścieżka do pliku JSON')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        #load placeholder images
        with open('static/core/img/placeholder125x125.png', 'rb') as file:
            ph125 = file.read()

        with open('static/core/img/placeholder150x150.png', 'rb') as file:
            ph150 = file.read()

        # Otwórz i wczytaj plik JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        try:
            # Otwórz i wczytaj plik JSON
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for l in data['leagues'].keys():
                #check if img is ''
                if (img_l := data['leagues'][l]['img']) != '':
                    img_l = base64.b64decode(img_l)
                else:
                    img_l = ph125
                #create league
                league, _ = League.objects.get_or_create(
                    name=l,
                    image=img_l
                )
                for t in data['leagues'][l]['teams'].keys():
                    if (img_t := data['leagues'][l]['teams'][t]['img']) != '':
                        img_t = base64.b64decode(img_t)
                    else:
                        img_t = ph125
                    team, _ = Team.objects.get_or_create(
                        name=t,
                        league=league,
                        image=img_t
                    )
                    for p in data['leagues'][l]['teams'][t]['players'].keys():
                        if (img_p := data['leagues'][l]['teams'][t]['players'][p]['img']) != '':
                            img_p = base64.b64decode(img_p)
                        else:
                            img_p = ph150
                        Player.objects.get_or_create(
                            name=p,
                            position=data['leagues'][l]['teams'][t]['players'][p]['position'],
                            team=team,
                            image=img_p
                        )

            self.stdout.write(self.style.SUCCESS('Data successfully imported'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Błąd podczas importowania danych: {str(e)}'))
