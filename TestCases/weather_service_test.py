import datetime as dt
import time
import unittest
import logging

import pytest
from services.weather_service import Forecast, WeatherProcessor, WeatherReading, TempUnit, SpeedUnit, weather_code
from services.address_service import Address, AddressProcessor
#from services.time_service import TimeService

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

class TestWeatherReading(unittest.TestCase):

    def setUp(self):
        """A baseline reading in Fahrenheit to reuse across tests."""
        self.reading_f = WeatherReading(
            location="Portland",
            temperature=32.0,
            wind_speed=10.0,
            temp_unit=TempUnit.FAHRENHEIT,
            speed_unit=SpeedUnit.MPH,
        )

    def test_fahrenheit_to_celsius(self):
        result = self.reading_f.temp_in(TempUnit.CELSIUS)
        self.assertAlmostEqual(result, 0.0, places=1)

    def test_celsius_to_fahrenheit(self):
        reading_c = WeatherReading(
            location="London",
            temperature=100.0,
            wind_speed=5.0,
            temp_unit=TempUnit.CELSIUS,
            speed_unit=SpeedUnit.KMPH,
        )
        result = reading_c.temp_in(TempUnit.FAHRENHEIT)
        self.assertAlmostEqual(result, 212.0, places=1)

    def test_same_unit_returns_unchanged(self):
        result = self.reading_f.temp_in(TempUnit.FAHRENHEIT)
        self.assertEqual(result, 32.0)

    def test_freezing_point(self):
        result = self.reading_f.temp_in(TempUnit.CELSIUS)
        self.assertAlmostEqual(result, 0.0, places=5)

    def test_body_temperature(self):
        reading = WeatherReading(
            location="Test", temperature=37.0, wind_speed=0,
            temp_unit=TempUnit.CELSIUS, speed_unit=SpeedUnit.MPH
        )
        self.assertAlmostEqual(reading.temp_in(TempUnit.FAHRENHEIT), 98.6, places=1)

    
    
    def test_WeatherIcon_0(self):
        icon = WeatherProcessor().getweatherdescription(0, weather_code.ICON)
        self.assertEqual(icon, "wi-day-sunny")

    def test_WeatherIcon_1(self):
        icon = WeatherProcessor().getweatherdescription(1,weather_code.ICON)
        self.assertEqual(icon, "wi-day-cloudy")
    def test_WeatherIcon_2(self):
        icon = WeatherProcessor().getweatherdescription(2,weather_code.ICON)
        self.assertEqual(icon, "wi-cloudy")

    def test_WeatherIcon_3(self):
        icon = WeatherProcessor().getweatherdescription(3,weather_code.ICON)  
        self.assertEqual(icon, "wi-fog")

    def test_WeatherIcon_45(self):
        icon = WeatherProcessor().getweatherdescription(45,weather_code.ICON)
        self.assertEqual(icon, "wi-fog")

    def test_WeatherIcon_48(self):
        icon = WeatherProcessor().getweatherdescription(48,weather_code.ICON)
        self.assertEqual(icon, "wi-rain-mix")
    def test_WeatherIcon_51(self):
        icon = WeatherProcessor().getweatherdescription(51,weather_code.ICON)
        self.assertEqual(icon, "wi-rain") 
    def test_WeatherIcon_53(self):
        icon = WeatherProcessor().getweatherdescription(53,weather_code.ICON)
        self.assertEqual(icon, "wi-rain")
    def test_WeatherIcon_55(self):
        icon = WeatherProcessor().getweatherdescription(55,weather_code.ICON)
        self.assertEqual(icon, "wi-rain")
    def test_WeatherIcon_61(self):
        icon = WeatherProcessor().getweatherdescription(61,weather_code.ICON)
        self.assertEqual(icon, "wi-rain")
    def test_WeatherIcon_63(self):
        icon = WeatherProcessor().getweatherdescription(63,weather_code.ICON)
        self.assertEqual(icon, "wi-rain")
    def test_WeatherIcon_65(self):
        icon = WeatherProcessor().getweatherdescription(65,weather_code.ICON)
        self.assertEqual(icon, "wi-rain")
    def test_WeatherIcon_71(self):
        icon = WeatherProcessor().getweatherdescription(71,weather_code.ICON)
        self.assertEqual(icon, "wi-snow")

class TestLocation:
    def test_validLocation(self):
        # partial Locatoin
        aproc = AddressProcessor()
        address = Address(city="Sandy", state="OR", zip_code="97055", country="US")
        wproc = WeatherProcessor()
        addressresponse = aproc.get_addressByPostalCode(address)
        weather_address = Address.from_api_response(addressresponse[0])
        weather_response = wproc.get_current(weather_address)
        current_weather = WeatherReading.from_api_response(weather_response[0], weather_address)
        # weather API returns a slightly different lat/lon
        assert current_weather.weather_snapshot > -1  # Ensure weather_code is present
        assert current_weather.lat == pytest.approx(45.394, abs=1e-2)  # Ensure latitude is correct
        assert current_weather.lon == pytest.approx(-122.246, abs=1e-2)  # Ensure longitude is correct

        

    def test_validLocation2(self):
        aproc = AddressProcessor()
        address = Address(street="37032 Salmonberry Street", city="Sandy", state="OR", zip_code="97055", country="US")
        wproc = WeatherProcessor()
        address_response = aproc.get_addressByPostalCode(address)
        weatheraddress = Address.from_api_response(address_response[0])
        weather_response = wproc.get_current(weatheraddress)
        current_weather = WeatherReading.from_api_response(weather_response[0], weatheraddress)
        assert current_weather.location == "37032 Salmonberry Street, Sandy, Oregon 97055"
        assert current_weather.lat == pytest.approx(45.412, abs=1e-2)
        assert current_weather.lon == pytest.approx(-122.293, abs=1e-2)

class TestForecasts:
    
    def test_weatherDateConstruct(self):
        todayforecast = Forecast(fc_date=dt.datetime.now(), temp=70.0, high=75.0, low=65.0)
        assert todayforecast.temp == 70.0
        assert todayforecast.high == 75.0
        assert todayforecast.low == 65.0
        assert todayforecast.weather_snapshot == 0

    def test_weatherDateTime(self):
        starttime = Forecast(fc_date=dt.datetime.now(), temp=70.0, high=75.0, low=65.0)
        time.sleep(3)  # Wait for 3 seconds
        endtime = Forecast(fc_date=dt.datetime.now(), temp=70)
        assert starttime.fc_date + dt.timedelta(seconds=3) <= endtime.fc_date  # The timestamps should be different since we waited for 3 seconds

    def test_forecast_from_api_response(self):
        forecast_data = {
            "time": ["2024-06-01", "2024-06-02", "2024-06-03"],
            "temperature_2m_max": [75.0, 80.0, 78.0],
            "temperature_2m_min": [60.0, 65.0, 62.0],
            "weather_code": [1, 2, 3]
        }
        forecast_list = WeatherReading.buildforecast(forecast_data)
        assert len(forecast_list) == 3
        assert forecast_list[0].fc_date == dt.datetime.strptime("2024-06-01", "%Y-%m-%d")
        assert forecast_list[0].high == 75.0
        assert forecast_list[0].low == 60.0
        assert forecast_list[0].weather_snapshot == 1



 

if __name__ == "__main__":
    unittest.main()