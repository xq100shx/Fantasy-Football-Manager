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
        return self.name.split()[-1]
    def get_dictionary(self):
        #get jpeg from db
        file = self.image
        
        return {'id': self.id, 'name': self.name, 'position': self.position, 'team': self.team.name}
