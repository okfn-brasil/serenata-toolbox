from async_lru import alru_cache

from serenata_toolbox import log


class Nominatim:
    """This abstraction wraps Open Street Maps's Nominatim API"""

    URL = "https://nominatim.openstreetmap.org/search/"

    @alru_cache(maxsize=2 ** 16)
    async def coordinates(self, session, **params):
        """Expected Nominatim params: street, city, state and postal"""
        params.update({"country": "Brazil", "format": "json"})
        async with session.get(self.URL, params=params) as response:
            log.debug(f"Getting coordinates for {response.url}…")
            data = await response.json()

        if not data:
            return {"latitude": None, "longitude": None}

        result, *_ = data
        return {"latitude": result["lat"], "longitude": result["lon"]}
