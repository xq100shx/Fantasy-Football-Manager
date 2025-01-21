from django.db import models

# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.CharField(max_length=100)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.position} - {self.team}'
    def get_surname(self):
        return self.name.split()[-1]

class Team(models.Model):
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=100)
    league = models.ForeignKey('League', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.league}'

class League(models.Model):
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=100)

    def __str__(self):
        return self.name