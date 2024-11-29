from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
import time
import redis
from os import environ
from educa.settings import REDIS_DB_HOST, REDIS_DB_NAME, REDIS_DB_PORT

"""
    Note: self.scope returns all data about the socket connection
"""
redis_client = redis.Redis(host=REDIS_DB_HOST, port=REDIS_DB_PORT, db=REDIS_DB_NAME)


def get_messages(course_id):
    key = f"mes_c{course_id}"
    messages = json.loads(redis_client.get(key) or b"{}")
    return messages


def delete_message(course_id, m_id, sender_id):
    messages = get_messages(course_id, sender_id)
    message_key = f"message_#{m_id}"

    if message_key in messages.keys():
        del messages[f"message_#{m_id}"]
        redis_client.set(message_key, json.dumps(messages))
    return 0


def save_message(message, course_id, ntime, sender_id, sender_name):
    key = f"mes_c{course_id}"
    message = {
        "message": message,
        "sender_id": sender_id,
        "sender": sender_name,
        "time": ntime,
        "cid": course_id,
    }
    messages = get_messages(course_id) or {}
    messages[f"message_#{messages.__len__()}"] = message
    redis_client.set(key, json.dumps(messages))


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
            message = data.get("message", None)

            if message:
                print("message received:", message)
                nano_time = data.get("nano_time")
                sender_id = self.user.id
                sender_name = self.user.username
                course_id = self.course_id
                save_message(message, course_id, nano_time, sender_id, sender_name)

                async_to_sync(self.channel_layer.group_send)(
                    self.course_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender": sender_name,
                        "time": nano_time,
                    },
                )

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))


class CallConsumer1(AsyncWebsocketConsumer):
    active_users = set()

    async def connect(self):
        # setting the group name
        self.room_name = self.scope["url_route"]["kwargs"]["course_id"]
        self.room_group_name = f"call-group-{self.room_name}"
        self.owner_key = f"owner_{self.room_group_name}"
        # adding the user to active users
        self.active_users.add(self.channel_name)
        # adding the user to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        # redis_client.flushall()
        # print("everything flused ....")
        # notifying other group memebers of this user's joining
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_joined", "user": self.channel_name}
        )

    async def disconnect(self, code):
        # removing the user from active users set
        print("disconnect from server....")
        self.active_users.remove(self.channel_name)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Notifying others
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_left", "user": self.channel_name}
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        type_ = data["type"]
        if type_ == "offer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_offer",
                    "offer": data["offer"],
                    "sender_name": data["senderName"],
                },
            )

        elif type_ == "answer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_answer",
                    "answer": data["answer"],
                    "sender_name": data["senderName"],
                    "his_offer": data["hisOffer"],
                },
            )
        elif type_ == "candidate":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_candidate",
                    "candidate": data["candidate"],
                    "sender_name": data["senderName"],
                },
            )
        elif type_ == "memberAllowed":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_member_allowed",
                    "member": data["member"],
                    "his_offer": data["hisOffer"],
                },
            )
        elif type_ == "callOwner":
            owner = json.loads(redis_client.get(self.owner_key) or b"{}")
            if owner:
                print("there was an owner", owner)
                owner = owner[self.owner_key]
            else:
                print("there was no owner, setting it....")
                owner = data["owner"]
                redis_client.set(self.owner_key, json.dumps({self.owner_key: owner}))

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "send_call_owner", "owner": owner},
            )
        elif type_ == "callEnd":
            print("call end")
            redis_client.delete(self.owner_key)
            print(
                "owner left the call, removed",
            )
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send_call_end"}
            )

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({"type": "joined", "user": event["user"]}))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({"type": "left", "user": event["user"]}))

    async def send_offer(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "offer",
                    "hisOffer": event["offer"],
                    "senderName": event["sender_name"],
                }
            )
        )

    async def send_candidate(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "candidate",
                    "candidate": event["candidate"],
                    "senderName": event["sender_name"],
                }
            )
        )

    async def send_answer(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "answer",
                    "answer": event["answer"],
                    "senderName": event["sender_name"],
                    "hisOffer": event["his_offer"],
                }
            )
        )

    async def send_member_allowed(self, event):
        print("member allow called ....")
        await self.send(
            text_data=json.dumps(
                {
                    "type": "memberAllowed",
                    "member": event["member"],
                    "hisOffer": event["his_offer"],
                }
            )
        )

    async def send_call_owner(self, event):
        await self.send(
            text_data=json.dumps({"type": "callOwner", "owner": event["owner"]})
        )

    async def send_call_end(self, event):
        await self.send(text_data=json.dumps({"type": "callEnd"}))


class CallConsumer2(AsyncWebsocketConsumer):
    active_users = set()

    async def connect(self):
        # setting the group name
        self.room_name = self.scope["url_route"]["kwargs"]["course_id"]
        self.room_group_name = f"call-group-{self.room_name}"

        # adding the user to active users
        self.active_users.add(self.channel_name)

        # adding the user to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # notifying other group memebers of this user's joining
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_joined", "user": self.channel_name,"users":list(self.active_users)}
        )

    async def disconnect(self, code):
        # removing the user from active users set
        print("disconnect from server....")
        self.active_users.remove(self.channel_name)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Notifying others
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_left", "user": self.channel_name}
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        type_ = data["type"]
        if type_ == "offer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_offer",
                    "offer": data["offer"],
                    "from": data["from"],
                    "to": data["to"]
                },
            )

        elif type_ == "answer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_answer",
                    "answer": data["answer"],
                    "from": data["from"],
                    "to": data["to"],
                },
            )
        elif type_ == "candidate":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_candidate",
                    "candidate": data["candidate"],
                    "from": data["from"],
                    "to": data["to"]
                },
            )

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({"type": "user_joined", "user": event["user"],"users":event["users"]}))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({"type": "left", "user": event["user"]}))

    async def send_offer(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "offer",
                    "offer": event["offer"],
                    "from": event["from"],
                    "to": event["to"]
                }
            )
        )

    async def send_candidate(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "candidate",
                    "candidate": event["candidate"],
                    "from": event["from"],
                    "to": event["to"]
                }
            )
        )

    async def send_answer(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "answer",
                    "answer": event["answer"],
                    "from": event["from"],
                    "to": event["to"],
                }
            )
        )
