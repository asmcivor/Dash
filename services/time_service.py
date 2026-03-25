from typing import Any
from datetime import datetime

# the logic for all of the time related features lives here, not in the routers.
# Routers call services; services know nothing about HTTP or HTMX.
class TimeService:
    async def get_current_time(self) -> dict[str, Any]:
        """
        Return the current server time.
        Replace with a real DB query or external API call if needed.
        """
        now = datetime.now()
        return {
            "current_time": now.strftime("%m/%d/%Y %H:%M"),
            "timestamp": int(now.timestamp()),
        }