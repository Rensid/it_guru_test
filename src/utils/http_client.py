import aiohttp
from typing import Any, Dict, Optional


class ExternalApiError(Exception):
    pass


class HttpUoW:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.bank = BankHttpClient(session=self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()


class BaseHttpClient:
    session: aiohttp.ClientSession
    base_url: str

    async def _request(self, method: str, path: str, **kwargs: Any):
        try:
            async with self.session.request(
                method, f"{self.base_url}{path}", **kwargs
            ) as response:
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    data = await response.text()

                if response.status >= 400:
                    raise ExternalApiError(data)
                return data
        except aiohttp.ClientError as e:
            raise ExternalApiError(f"connection error: {e}") from e


class BankHttpClient(BaseHttpClient):
    def __init__(self, session: aiohttp.ClientSession):
        self.base_url = "bank.api"
        self.session = session

    async def acquiring_start(self, order_id: int, amount: float) -> str:
        data = await self._request(
            "POST",
            "/acquiring_start",
            json={"order_id": order_id, "amount": amount},
        )
        if isinstance(data, dict) and "payment_id" in data:
            return data["payment_id"]
        raise ExternalApiError(data)

    async def acquiring_check(self, payment_id: str) -> Dict[str, Any]:
        data = await self._request(
            "GET",
            "/acquiring_check",
            params={"payment_id": payment_id},
        )
        if isinstance(data, dict) and "payment_id" in data:
            return data
        raise ExternalApiError(data)
