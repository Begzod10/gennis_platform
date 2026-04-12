from tasks.admin.vats.services.client import VatsCRMClient


class VatsProcess:
    def __init__(self):
        self.client = VatsCRMClient()

    async def call(self, user, phone):
        return await self.client.make_call(user, phone)
