from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSquadSerializer
from core.models import UserSquad, UserSquadPlayer


@api_view(['POST'])
def save_squad(request):
    # Handle POST requests to save a user's squad
    if request.method == 'POST':
        # Deserialize and validate incoming data using the UserSquadSerializer
        serializer = UserSquadSerializer(data=request.data)

        # Check if the data is valid according to the model's requirements
        if serializer.is_valid():
            # Save the validated data to the database
            serializer.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)

        # If validation fails, return the error details
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # If the request method is not POST, return a 405 error
    return Response({'success': False, 'message': 'Invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
def update_squad(request, squad_id):
    try:
        # Retrieve the existing squad by ID
        squad = UserSquad.objects.get(id=squad_id, user=request.user)
    except UserSquad.DoesNotExist:
        return Response({'success': False, 'message': 'Squad not found'}, status=status.HTTP_404_NOT_FOUND)

    # Deserialize and validate incoming data using the UserSquadSerializer
    serializer = UserSquadSerializer(squad, data=request.data, partial=True)

    # Check if the data is valid according to the model's requirements
    if serializer.is_valid():
        # Save the validated data to the database
        serializer.save()
        return Response({'success': True}, status=status.HTTP_200_OK)

    # If validation fails, return the error details
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def check_existing_squad(request):
    # Retrieve the currently authenticated user
    user = request.user

    # Fetch the latest squad for the user, ordered by the most recent date
    squad = UserSquad.objects.filter(user=user).order_by('-date').first()

    # If a squad exists, fetch its associated players
    if squad:
        players = UserSquadPlayer.objects.filter(user_squad=squad).select_related('player')

        # Prepare the response data, including player details
        squad_data = {
            'formation': squad.formation,
            'players': [
                {
                    'id': p.player.id,
                    'name': p.player.name,
                    'position': p.position,
                    'team': p.player.team.name,
                    'points': p.points
                } for p in players
            ]
        }
        return Response({'hasSquad': True, 'squad': squad_data})

    # If no squad exists, return a flag indicating no squad
    return Response({'hasSquad': False})