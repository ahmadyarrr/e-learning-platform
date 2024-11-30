import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template import Template
from django.template.context import Context
from notification.models import Notification
from asgiref.sync import sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # setting the consumer group name
        self.notf_for = self.scope["url_route"]["kwargs"]["for"]
        self.id = None
        self.group_name = f"notf_{self.notf_for}"
        if self.notf_for in ("students", "instructors"):
            self.id = self.scope["url_route"]["kwargs"]["id"]
            self.group_name = f"notf_{self.notf_for}_{self.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        # here we are receving all details of the notification using JSON
        data = json.loads(text_data)
        if data["type"] == "share_notf":
            notf_id = int(data["notf_id"])
            notification = await Notification.objects.aget(id=notf_id)
            template = Template(
                '<li><a class="notf-link" data-notification_id={{notification.id}} href="{{notification.related_object.get_absolute_url}}">{{notification.text}}</a></li>'
            )
            context = Context({"notification": notification})
            rendered_notf = await sync_to_async(template.render)(context=context)
            await self.channel_layer.group_send(
                self.group_name, {"type": "share_notf", "notf": rendered_notf}
            )

    async def disconnect(self, code):
        return await super().disconnect(code)

    async def share_notf(self, event):
        await self.send(
            text_data=json.dumps({"type": "recv_notf", "notf": event["notf"]})
        )
