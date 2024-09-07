from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from django.utils.timezone import now

"""
    Note: self.scope returns all data about the socket connection
"""


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # getting the course name and making its group name
        self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
        self.course_group_name = "course_group" + self.course_id
        # joining the group room
        await self.channel_layer.group_add(self.course_group_name,
                                           self.channel_name)
        self.user = self.scope["user"]
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.course_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            message = data["message"]
            print("message received:", message)
            # broadcasting the message
            await self.channel_layer.group_send(
                self.course_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.user.username,
                    "time": now().isoformat(),
                },
            )

    async def chat_message(self, event):
        print(event, "=----event valu in chat_message")
        # event is ....
        await self.send(text_data=json.dumps(event))