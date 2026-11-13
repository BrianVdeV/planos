# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # 1. Si no está logueado, rechazamos la conexión WebSocket
        if self.user.is_anonymous:
            await self.close()
            return

        # 2. Definimos a qué grupos se unirá este usuario
        self.groups_to_join = [
            "global_notifications",                  # Para avisos a toda la empresa
            # Para avisos privados al usuario
            f"user_notifications_{self.user.id}"
        ]

        # 3. Si es administrador, lo unimos al grupo de admins
        if self.user.is_staff or self.user.is_superuser:
            self.groups_to_join.append("admin_notifications")

        # 4. Suscribimos al usuario a todos sus grupos
        for group in self.groups_to_join:
            await self.channel_layer.group_add(group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Al desconectarse, lo sacamos de todos los grupos
        if hasattr(self, 'groups_to_join'):
            for group in self.groups_to_join:
                await self.channel_layer.group_discard(group, self.channel_name)

    # 5. EVENTO GENÉRICO: Este método maneja TODOS los mensajes, sea el modelo que sea
    async def send_notification(self, event):
        # Extraemos la data enviada desde Django y la mandamos al cliente JS
        await self.send(text_data=json.dumps(event["data"]))
