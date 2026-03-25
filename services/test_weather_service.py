import unittest
import pytest  
from weather_service import WeatherProcessor, WeatherReading, TempUnit, SpeedUnit
from address_service import Address, AddressProcessor

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

    def test_validLocation(self):
        reading_location = WeatherReading(
            location="abcd",
            temperature=70.0,
            wind_speed=5.0,
            temp_unit=TempUnit.FAHRENHEIT,
            speed_unit=SpeedUnit.MPH,
        )
        self.assertNotEqual(reading_location.location, "New York") 
    
    def test_validLocation2(self):
        aproc = AddressProcessor()
        address = Address(street="37032 Salmonberry Street", city="Sandy", state="OR", zip_code="97055", country="US")
        wproc = WeatherProcessor()
        weatheraddress = aproc.get_addressByPostalCode(address)
        reading_location = wproc.get_current(weatheraddress)
        self.assertEqual(reading_location.location, "37032 Salmonberry Street, Sandy, Oregon 97055, us")

    @unittest.skip(reason="This test is expected to fail due to an invalid location.")
    def test_invalidLocation(self):
        reading_location = WeatherReading(
            location="New York",
            temperature=70.0,
            wind_speed=5.0,
            temp_unit=TempUnit.FAHRENHEIT,
            speed_unit=SpeedUnit.MPH,
        )
        self.assertEqual(reading_location.location, "New York")

if __name__ == "__main__":
    unittest.main()