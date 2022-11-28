'''View module for handeling requests about events'''

from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Gamer, Game, EventGamer
from rest_framework.decorators import action


class EventView(ViewSet):
    '''Levelup event types view'''
    
    def retrieve(self, request, pk):

        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request):
        """Handle GET requests to get all game types"""
        
        events = Event.objects.all()
        
        event_game = request.query_params.get('game', None)
        if event_game is not None:
            events = events.filter(game = event_game)
            
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        ''''handles POST operations'''
        
        gamer = Gamer.objects.get(id=request.data["organizer"])
        game = Game.objects.get(pk=request.data["game"])
        
        event = Event.objects.create(
            game = game,
            description = request.data['description'],
            date = request.data['date'],
            time = request.data['time'],
            organizer = gamer,
        )
        serializer = EventSerializer(event)
        return Response(serializer.data)
    
    def update(self, request, pk):
        """Handles PUT requests for an event"""
        
        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        game = Game.objects.get(pk=request.data["game"])
        event.game = game
        
        event.save()
        
        return Response(None, status=status.HTTP_204_NO_CONTENT) 
    
    def destroy(self, request, pk):
        '''Handles delete request for events'''
        
        event=Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""

        gamer = Gamer.objects.get(pk=request.data["user_id"])
        event = Event.objects.get(pk=pk)
        EventGamer.objects.create(
            gamer = gamer,
            event = event,
        )
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)
    
    @action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Delete request for gamer leaving event"""
        
        gamer = Gamer.objects.get(pk=request.data["user_id"])
        event = Event.objects.get(pk=pk)
        event_gamer = EventGamer.objects.get(event=event, gamer=gamer)
        event_gamer.delete()
        
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer"""
    class Meta:
        model = Event
        fields = ('id', 'game', 'description', 'date', 'time', 'organizer')
        depth = 1
