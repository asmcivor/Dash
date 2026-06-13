"""
WeatherProcessor — Python class template for fetching and processing weather data.

Fields:
  - temperature   (°F or °C)
  - wind_speed    (mph or km/h)

API calls are designed to be triggered via HTMX endpoints.
Wire up each public method to a Flask/FastAPI route and point
your HTMX attributes at those routes.
"""

from __future__ import annotations

import time

from fastapi import logger
#from services.address_service import Address, AddressProcessor # Import the Address class from the address_service module
from services.address_service import Address, AddressProcessor   
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import urllib.request
import urllib.parse
import json
import logging
from venv import logger

#logging setup
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("app.log", mode="a")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# ---------------------------------------------------------------------------
# Supporting types
# ---------------------------------------------------------------------------

class TempUnit(str, Enum):
    CELSIUS    = "celsius"
    FAHRENHEIT = "fahrenheit"

class TempChar(str, Enum):
    C = "C"
    F = "F"

class SpeedUnit(str, Enum):
    MPH  = "mph"
    KMPH = "kmh"

class weather_code(str,Enum):
    TEXT = "text"
    ICON = "icon"


@dataclass
class WeatherReading:
    """A single weather observation snapshot."""
    location:       str
    lat:            float = 0.0
    lon:            float = 0.0
    temperature:    float
    wind_speed:     float
    temp_unit:      TempUnit  = TempUnit.FAHRENHEIT
    temp_char:      TempChar = TempChar.F
    speed_unit:     SpeedUnit = SpeedUnit.MPH
    description:    str       = ""
    humidity:       float | None = None   # percent value is a float with no default value and none is acceptable
    timestamp:      float     = field(default_factory=time.time)
    elevation:      float     = 0.0   # gets the time with every creation of the object
    
    @classmethod
    def from_api_response(cls, data: dict) -> WeatherReading:
        logger.debug("Processing API response: %s", data)
        weather_units = data.get("current_units", {})
        weather_current = data.get("current", {})

        try:
            return cls(
            location=data.get("location", ""),
            temperature=weather_current.get("temperature_2m", 0.0),
            wind_speed=weather_current.get("wind_speed_10m", 0.0),
            # update this section to handle C/F
            temp_unit=TempUnit.FAHRENHEIT,
            temp_char=TempChar.F,
            speed_unit=SpeedUnit.MPH,
            description=data.get("description", ""),
            humidity=data.get("humidity",""),
            lat=data.get("latitude", 0.0),
            lon=data.get("longitude", 0.0),
            )
        except (ValueError, TypeError) as e:
            logger.error("Error processing API response: %s", e)
            return None
    
    # --- convenience conversions -------------------------------------------

    def temp_in(self, unit: TempUnit) -> float:
        """Return temperature converted to the requested unit."""
        if unit == self.temp_unit:
            return self.temperature
        if unit == TempUnit.CELSIUS:
            return (self.temperature - 32) * 5 / 9   # F → C
        return self.temperature * 9 / 5 + 32          # C → F

    def wind_in(self, unit: SpeedUnit) -> float:
        """Return wind speed converted to the requested unit."""
        if unit == self.speed_unit:
            return self.wind_speed
        if unit == SpeedUnit.KMPH:
            return self.wind_speed * 1.60934           # mph → km/h
        return self.wind_speed / 1.60934               # km/h → mph

    def to_dict(self) -> dict:
        return {
            "location":    self.location,
            "temperature": self.temperature,
            "temp_unit":   self.temp_unit.value,
            "wind_speed":  self.wind_speed,
            "speed_unit":  self.speed_unit.value,
            "description": self.description,
            "humidity":    self.humidity,
            "timestamp":   self.timestamp,
        }


# ---------------------------------------------------------------------------
# Main processor class
# ---------------------------------------------------------------------------

class WeatherProcessor:
    """
    Fetch, store, and process weather data.

    Typical HTMX integration
    ------------------------
    Each public method maps to one HTTP endpoint.  Example (Flask):

        @app.get("/weather/current")        → processor.get_current(location)
        @app.get("/weather/history")        → processor.get_history()
        @app.post("/weather/units")         → processor.set_units(temp, speed)
        @app.get("/weather/alert")          → processor.check_alerts()

    Wire the routes to HTMX like:
        hx-get="/weather/current?location=London"
        hx-trigger="load, every 5m"
        hx-target="#weather-panel"
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        api_key:    str        = "",
        temp_unit:  TempUnit   = TempUnit.FAHRENHEIT,
        speed_unit: SpeedUnit  = SpeedUnit.MPH,
        history_limit: int     = 50,
    ) -> None:
        self.api_key       = api_key
        self.temp_unit     = temp_unit
        self.speed_unit    = speed_unit
        self.history_limit = history_limit
        self._history:     list[WeatherReading] = []
        self._latest:      WeatherReading | None = None

    # ------------------------------------------------------------------
    # Public API — each method is one HTMX endpoint
    # ------------------------------------------------------------------

    def get_current(self, location: Address) -> WeatherReading:
        """
        Fetch current weather for *location* and cache it.

        HTMX:  hx-get="/weather/current?location={location}"
        """
        reading = self._fetch_from_api(location)
        if reading is None:
            raise ValueError(f"Could not fetch weather for location: {location}")
            return None
        
        self._latest = reading
        self._add_to_history(reading)
        return reading

    def get_history(
        self,
        limit: int = 10,
        location: str | None = None,
    ) -> list[WeatherReading]:
        """
        Return cached history, newest first.

        HTMX:  hx-get="/weather/history?limit=10"
        """
        results = self._history[::-1]          # newest first
        if location:
            results = [r for r in results if r.location.lower() == location.lower()]
        return results[:limit]

    def set_units(
        self,
        temp_unit:  TempUnit  = TempUnit.FAHRENHEIT,
        speed_unit: SpeedUnit = SpeedUnit.MPH,
    ) -> dict:
        """
        Update display units; returns the latest reading in new units.

        HTMX:  hx-post="/weather/units"  hx-vals='{"temp_unit":"celsius"}'
        """
        self.temp_unit  = temp_unit
        self.speed_unit = speed_unit
        if self._latest:
            return self._format_reading(self._latest)
        return {"status": "no data yet"}

    def check_alerts(
        self,
        temp_high: float = 95.0,    # °F
        temp_low:  float = 20.0,    # °F
        wind_high: float = 40.0,    # mph
    ) -> list[str]:
        """
        Return a list of human-readable alert strings for the latest reading.

        HTMX:  hx-get="/weather/alert"  hx-trigger="every 10m"
        """
        if not self._latest:
            return []

        reading = self._latest
        alerts: list[str] = []

        temp_f = reading.temp_in(TempUnit.FAHRENHEIT)
        wind_m = reading.wind_in(SpeedUnit.MPH)

        if temp_f >= temp_high:
            alerts.append(f"🌡️ High temperature alert: {temp_f:.1f}°F at {reading.location}")
        if temp_f <= temp_low:
            alerts.append(f"❄️ Low temperature alert: {temp_f:.1f}°F at {reading.location}")
        if wind_m >= wind_high:
            alerts.append(f"💨 High wind alert: {wind_m:.1f} mph at {reading.location}")

        return alerts

    def summarize(self) -> dict:
        """
        Aggregate stats across all cached history entries.

        HTMX:  hx-get="/weather/summary"
        """
        if not self._history:
            return {"error": "No data available"}

        temps  = [r.temp_in(TempUnit.FAHRENHEIT) for r in self._history]
        winds  = [r.wind_in(SpeedUnit.MPH) for r in self._history]

        return {
            "count":        len(self._history),
            "avg_temp_f":   round(sum(temps) / len(temps), 1),
            "max_temp_f":   round(max(temps), 1),
            "min_temp_f":   round(min(temps), 1),
            "avg_wind_mph": round(sum(winds) / len(winds), 1),
            "max_wind_mph": round(max(winds), 1),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_from_api(self, location: Address) -> WeatherReading:
        """
        Call the weather API and return a WeatherReading.

        Replace the body of this method to point at your real provider
        (OpenWeatherMap, WeatherAPI, Open-Meteo, etc.).
        The stub below calls Open-Meteo's free geocoding + forecast API
        — no key required, good for development.
        """
        

        # --- 2. Fetch current conditions from the locatoin lat long in the address block--------
        wx_url = (
            "https://api.open-meteo.com/v1/forecast?"
            + urllib.parse.urlencode({
                "latitude":  location.lat,
                "longitude": location.lon,
                "current":   "temperature_2m,wind_speed_10m,relative_humidity_2m,weather_code",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit":  "mph",
                "timezone":  "auto",
                "forecast_days": 1,
            })
        )
        with urllib.request.urlopen(wx_url, timeout=10) as resp:
            wx_data = json.loads(resp.read())

        current = wx_data["current"]

        return WeatherReading(
            location    = f"{location.street}, {location.city}, {location.state} {location.zip_code}, {location.country}",
            temperature = current["temperature_2m"],
            wind_speed  = current["wind_speed_10m"],
            temp_unit   = TempUnit.FAHRENHEIT,
            speed_unit  = SpeedUnit.MPH,
            humidity    = current.get("relative_humidity_2m"),
            description = self._weather_code_to_text(current.get("weather_code", 0)),
        )

    def _add_to_history(self, reading: WeatherReading) -> None:
        self._history.append(reading)
        if len(self._history) > self.history_limit:
            self._history.pop(0)

    def _format_reading(self, reading: WeatherReading) -> dict:
        d = reading.to_dict()
        d["temperature"] = round(reading.temp_in(self.temp_unit), 1)
        d["temp_unit"]   = self.temp_unit.value
        d["wind_speed"]  = round(reading.wind_in(self.speed_unit), 1)
        d["speed_unit"]  = self.speed_unit.value
        return d


# ---------------------------------------------------------------------------
# Utility: WMO weather-code → description
# ---------------------------------------------------------------------------
    def getweatherdescription(self, code: int, weather_type: str) -> str:
        _WeatherMAP = {
        0: {"text": "Clear sky", "icon": "wi-day-sunny"},
        1: {"text": "Mainly clear", "icon": "wi-day-cloudy"},
        2: {"text": "Partly cloudy", "icon": "wi-cloudy"},
        3: {"text": "Overcast", "icon": "wi-fog"},
        45: {"text": "Fog", "icon": "wi-fog"},
        48: {"text": "Rime fog", "icon": "wi-rain-mix"},
        51: {"text": "Light drizzle", "icon": "wi-rain"},
        53: {"text": "Drizzle", "icon": "wi-rain"},
        55: {"text": "Heavy drizzle", "icon": "wi-rain"},
        61: {"text": "Light rain", "icon": "wi-rain"},
        63: {"text": "Rain", "icon": "wi-rain"},
        65: {"text": "Heavy rain", "icon": "wi-rain"},
        71: {"text": "Light snow", "icon": "wi-snow"},
        73: {"text": "Snow", "icon": "wi-snow"},
        75: {"text": "Heavy snow", "icon": "wi-snow"},
        95: {"text": "Thunderstorm", "icon": "wi-thunderstorm"},
        96: {"text": "Thunderstorm w/ hail", "icon": "wi-thunderstorm"},
        99: {"text": "Heavy thunderstorm", "icon": "wi-thunderstorm"},
        }
        return _WeatherMAP.get(code, {"text": f"Unknown code {code}", "icon": f"Unknown code {code}"}).get(weather_type)

    def _weather_code_to_text(self, code: int) -> str:
    # create a dictionary that maps the weather codes to their correspond text and icon
    # descriptions
        _MAP = {
        0: "Clear sky", 
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog",
        51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
        61: "Light rain", 63: "Rain", 65: "Heavy rain",
        71: "Light snow", 73: "Snow", 75: "Heavy snow",
        80: "Rain showers", 81: "Showers", 82: "Heavy showers",
        95: "Thunderstorm", 96: "Thunderstorm w/ hail", 99: "Heavy thunderstorm",
        }
        return _MAP.get(code, f"Weather code {code}")


# ---------------------------------------------------------------------------
# Quick smoke-test  (python weather_processor.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    setup_logging()
    wproc = WeatherProcessor()
    

    
