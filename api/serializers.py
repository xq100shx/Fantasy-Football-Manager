from rest_framework import serializers
from core.models import UserSquad, UserSquadPlayer

class UserSquadPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSquadPlayer
        fields = ['player', 'position']

class UserSquadSerializer(serializers.ModelSerializer):
    players = UserSquadPlayerSerializer(many=True)

    class Meta:
        model = UserSquad
        fields = ['user', 'date', 'score', 'locked','formation' ,'players']

    def create(self, validated_data):
        players_data = validated_data.pop('players')
        user_squad = UserSquad.objects.create(**validated_data)
        for player_data in players_data:
            UserSquadPlayer.objects.create(user_squad=user_squad, **player_data)
        return user_squad