from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .encryption import *
from .models import Room, Message


@login_required
def rooms(request):
    rooms = Room.objects.all()

    return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def room(request, slug):
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)
    total_msgs = len(messages)
    if total_msgs > 25:
        last_msgs = messages[total_msgs-25::]
    else:
        last_msgs = messages

    for msg in last_msgs:
        print(msg.content)
        msg.content = decrypt(msg.content)
        print(msg.content)

    return render(request, 'room/room.html', {'room': room, 'messages': last_msgs})