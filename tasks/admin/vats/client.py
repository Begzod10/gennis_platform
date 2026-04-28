import aiohttp
from tasks.admin.vats import settings


class VatsCRMClient:
    def __init__(self):
        self.base_url = f"https://{settings.VATS_DOMAIN}/crmapi/v1"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-KEY": settings.VATS_API_KEY
        }

    async def request(self, method: str, endpoint: str,
                      data: dict = None, params: dict = None) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
            ) as resp:
                try:
                    return await resp.json()
                except Exception as e:
                    print(f"JSON parse error: {e}")
                    return {"error": str(e)}

    async def make_call(self, user: str, phone: str) -> dict:
        return await self.request(
            "POST", "/makecall",
            data={"user": user, "phone": phone}
        )

    async def get_call_info_by_id(self, callid: str):
        """
        None qaytarsa - hali tugamagan
        dict qaytarsa - tugagan
        """
        result = await self.request(
            "GET", "/history/json",
            params={"uid": callid}
        )
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
