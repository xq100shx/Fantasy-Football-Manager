import base64

from django.db import models

# Create your models here.
class League(models.Model):
    name = models.CharField(max_length=100)
    image = models.BinaryField()

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey('League', on_delete=models.CASCADE)
    image = models.BinaryField()

    def __str__(self):
        return f'{self.name} - {self.league}'

class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    image = models.BinaryField()
    def __str__(self):
        return f'{self.name} - {self.position} - {self.team}'
    def get_surname(self):
        if len(self.name.split()) == 1:
            return self.name
        #else return everything but first element
        return ' '.join(self.name.split()[1:])
    def get_dictionary(self):
        return {'id': self.id, 'name': self.name, 'position': self.position, 'team': self.team.name}

class UpcomingMatch(models.Model):
    game_week = models.IntegerField()
    home_team = models.ForeignKey('Team', related_name='home_team', on_delete=models.CASCADE)
    away_team = models.ForeignKey('Team', related_name='away_team', on_delete=models.CASCADE)
    date = models.DateField()
    def __str__(self):
        return f'{self.home_team} vs {self.away_team}'

    def get_dictionary(self):
        league_class = self.home_team.league.name.lower().replace(' ', '-')
        return {
            'game_week': self.game_week,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'date': self.date,
            'league': self.home_team.league.name,
            'league_class': league_class
        }

class UserSquadPlayer(models.Model):
    user_squad = models.ForeignKey('UserSquad', on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    position = models.CharField(max_length=10,default='GK')

class UserSquad(models.Model):
    #one user can have many squads
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    #we need to store date of squad creation
    date = models.DateField()
    #we will be adding points to the squad after each match
    score = models.IntegerField()
    #before game_week starts we lock the squad so that user can't change it
    locked = models.BooleanField()
    #we will be storing the formation of the squad
    formation = models.CharField(max_length=10,default='4-4-2')