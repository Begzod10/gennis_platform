import httpx
from tasks.admin.vats import settings


class VatsCRMClient:
    def __init__(self):
        self.base_url = f"https://{settings.VATS_DOMAIN}/crmapi/v1"
        self.headers = {
            "X-API-KEY": settings.VATS_API_KEY,
            "Content-Type": "application/json"
        }

    async def request(self, method, endpoint, data=None, params=None):
        async with httpx.AsyncClient() as client:
            res = await client.request(
                method,
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=data,
                params=params
            )
            try:
                return res.json()
            except:
                return {"error": "Invalid JSON"}

    async def make_call(self, user, phone):
        return await self.request(
            "POST",
            "makecall",
            data={"user": user, "phone": phone}
        )
