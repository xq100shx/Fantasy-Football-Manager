from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSquadSerializer
from core.models import UserSquad, UserSquadPlayer

@api_view(['POST'])
def save_squad(request):
    if request.method == 'POST':
        serializer = UserSquadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'success': False, 'message': 'Invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def check_existing_squad(request):
    user = request.user
    squad = UserSquad.objects.filter(user=user).order_by('-date').first()
    if squad:
        players = UserSquadPlayer.objects.filter(user_squad=squad).select_related('player')
        squad_data = {
            'formation': squad.formation,
            'players': [{'id': p.player.id, 'name': p.player.name, 'position': p.position, 'team': p.player.team.name,'points':p.points} for p in players]
        }
        return Response({'hasSquad': True, 'squad': squad_data})
    return Response({'hasSquad': False})