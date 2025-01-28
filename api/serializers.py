from rest_framework import serializers
from core.models import UserSquad, UserSquadPlayer

# Serializer for the UserSquadPlayer model, which represents an individual player in the user's squad
class UserSquadPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSquadPlayer
        # Fields to be serialized
        fields = ['player', 'position', 'points']

# Serializer for the UserSquad model, which represents the full squad of a user
class UserSquadSerializer(serializers.ModelSerializer):
    # Nested serializer to handle the list of players in the squad
    players = UserSquadPlayerSerializer(many=True)

    class Meta:
        model = UserSquad
        # Fields to be serialized
        fields = ['user', 'date', 'score', 'locked', 'formation', 'players']

    # Custom method to handle creation of nested objects
    def create(self, validated_data):
        # Extract player data from the validated data
        players_data = validated_data.pop('players')

        # Create the UserSquad object without player data
        user_squad = UserSquad.objects.create(**validated_data)

        # Iterate over the list of player data and create related UserSquadPlayer entries
        for player_data in players_data:
            # Create each player and associate them with the created UserSquad
            UserSquadPlayer.objects.create(user_squad=user_squad, **player_data)

        # Return the created UserSquad object
        return user_squad