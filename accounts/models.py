from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.username
    def get_points(self):
        return {
            'username': self.username,
            'score': self.score
        }