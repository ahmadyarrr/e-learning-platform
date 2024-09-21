from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from django.utils.timezone import now

"""
    Note: self.scope returns all data about the socket connection
"""


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        # getting the course name and making its group name
        self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
        self.course_group_name = "course_group" + self.course_id
        async_to_sync(self.channel_layer.group_add)(
            self.course_group_name, self.channel_name
        )
        self.user = self.scope["user"]
        self.accept()

    def disconnect(self, code):
        async_to_sync(
            self.channel_layer.group_discard(self.course_group_name, self.channel_name)
        )

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            message = data["message"]
            print("message received:", message)
            # self.send(text_data=json.dumps({"typee": "message", "message": message}))
            # sending the message to the whole group members
            async_to_sync(self.channel_layer.group_send)(
                self.course_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.user.username,
                    "time": now().isoformat(),
                },
            )

    def chat_message(self, event):
        print(event, "=----event valu in chat_message")
        self.send(text_data=json.dumps(event))


class CallConsumer(AsyncWebsocketConsumer):
    active_users = set()

    async def connect(self):
        # setting the group name
        self.room_name = self.scope['url_route']['course_id']
        self.room_group_name = f"call_{self.room_name}"
        # adding the user to active users
        self.active_users.add(self.channel_name)
        
        # adding the user to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # notifying other group memebers of this user's joining
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_joined", "user": self.channel_name}
        )

    async def disconnect(self, code):
        # removing the user from active users set
        print('disconnect from server....')
        self.active_users.remove(self.channel_name)

        self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Notifying others
        self.channel_layer.group_send(
            self.room_group_name, {"type": "user_left", "user": self.channel_name}
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if "offer" in data:
            self.channel_layer.group_send(
                self.room_group_name,
                {"type": "offer", "offer": data["offer"], "user": self.channel_name},
            )

        elif "answer" in data:
            self.channel_layer.group_send(
                self.room_group_name,
                {"type": "answer", "answer": data["answer"], "user": self.channel_name},
            )
        elif "candidate" in data:
            self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "candidate",
                    "candidate": data["candidate"],
                    "user": self.channel_name,
                },
            )

    async def user_joined(self, event):
        print('user joined called on server')
        await self.send(
            text_data=json.dumps({"type": "user_joined", "user": event["user"]})
        )

    async def user_left(self, event):
        print('user left called on server')
        
        await self.send(
            text_data=json.dumps({"type": "user_left", "user": event["user"]})
        )

    async def offer(self, event):
        print('offer called on server')

        await self.send(
            text_data=json.dumps(
                {"type": "offer", "offer": event["offer"], "user": event["user"]}
            )
        )

    async def candidate(self, event):
        print('candidate called on server')
        await self.send(
            text_data=json.dumps(
                {
                    "type": "candidate",
                    "candidate": event["candidate"],
                    "user": event["user"],
                }
            )
        )

    async def answer(self, event):
        print('answer called on server')
        await self.send( 
            text_data=json.dumps(
                {"type": "answer", "answer": event["answer"], "user": event["user"]}
            )
        )
