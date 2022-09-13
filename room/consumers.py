import json

from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .encryption import *

from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('WebSocket Connected')
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    # Receive message from WebSocket
    async def receive(self, text_data):
        print('Message received')
        data = json.loads(text_data)
        message = encrypt(data['message'])
        username = data['username']
        room = data['room']
        print(message)
        print( username)
        print( room)
        
        # this message needs to be encrypted
        await self.save_message(username, room, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': decrypt(message),
                'username': username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        print('chat_message received')
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    async def disconnect(self,close_code):
        print('WebSocket Disconnected')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )    

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)

        Message.objects.create(user=user, room=room, content=message)