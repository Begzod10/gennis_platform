import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CallStatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.callid = self.scope['url_route']['kwargs']['callid']
        self.group_name = f"call_{self.callid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def call_status(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "status": "s"
        }))

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            "echo": text_data
        }))

    async def disconnect(self, close_code):
        print("Disconnected:", close_code)