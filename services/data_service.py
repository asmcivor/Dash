"""
DataService: all business logic lives here, not in the routers.
Routers call services; services know nothing about HTTP or HTMX.
Swap out the internals (DB, external API, cache) without touching routes.
"""

from typing import Any


class DataService:
    async def get_reports(self) -> list[dict[str, Any]]:
        """
        Fetch a list of reports for the dashboard.
        Replace with a real DB query or external API call.
        """
        return [
            {"id": 1, "title": "Sales Report", "created_at": "2024-01-01"},
            {"id": 2, "title": "User Activity", "created_at": "2024-01-02"},
            {"id": 3, "title": "Error Logs", "created_at": "2024-01-03"},
        ]
    
    async def get_stats(self) -> dict[str, Any]:
        """
        Fetch summary statistics for the dashboard.
        Replace with a real DB query or external API call.
        """
        return {
            "total_users": 1_284,
            "active_sessions": 42,
            "revenue_today": 8_320.50,
            "error_rate": 0.3,
        }

    async def get_table_data(
        self, page: int = 1, limit: int = 20
    ) -> tuple[list[dict], int]:
        """
        Return paginated rows and the total count.
        Replace with: rows = await db.fetch_all(query.offset(...).limit(...))
        """
        # Simulated data
        total = 100
        offset = (page - 1) * limit
        rows = [
            {"id": i, "name": f"Item {i}", "status": "active", "value": i * 10.5}
            for i in range(offset + 1, min(offset + limit + 1, total + 1))
        ]
        return rows, total

    async def create_item(self, data: dict) -> dict:
        """
        Persist a new item and return the created record.
        Replace with a real INSERT and return the DB record.
        """
        return {"id": 999, **data, "status": "active"}
