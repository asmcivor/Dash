from datetime import datetime
import time
import pytest

from services.time_service import TimeService


class TestTimeService:
    def test_get_current_time(self):
        time_service = TimeService()
        current_time_data = time_service.get_current_time()
        assert current_time_data.timestamp() <= datetime.now().timestamp()
        
    def test_get_current_date(self):
        time_service = TimeService()
        current_date = time_service.get_current_date()
        assert current_date.day == datetime.now().day

if __name__ == "__main__":
        time_data = TimeService().get_current_time()
        print(time_data)
        date_data = TimeService().get_current_date()
        print(f"Just the date part: {date_data}")