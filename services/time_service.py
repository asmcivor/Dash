from typing import Any
from datetime import datetime

# the logic for all of the time related features lives here, not in the routers.
# Routers call services; services know nothing about HTTP or HTMX.
class TimeService:
    def get_current_time(self) -> datetime:
        
        return datetime.now()
     
    def get_current_date(self) -> datetime:
        return datetime.now().date()

if __name__ == "__main__":
        time_data = TimeService().get_current_time()
        print(time_data)
        date_data = TimeService().get_current_date()
        print(f"Just the date part: {date_data}")
