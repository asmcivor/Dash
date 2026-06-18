from __future__ import annotations

from operator import add
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import urllib.request
import urllib.parse
from urllib.parse import urlencode, quote
from functools import partial
import json
import logging
from venv import logger
from config import settings

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

@dataclass
class Address:
    house_number: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    ISO_state: str | None = None
    lat: float | None = None
    lon: float | None = None

    @classmethod
    def from_api_response(cls, raw: dict) -> "Address":
        logger.debug("mapping api response to Address: %s", raw)
        address_detail = raw.get("address", {})

        try:
            return cls(
                house_number =address_detail.get("house_number", ""),
                street=address_detail.get("road", ""), 
                city=address_detail.get("city", "") or address_detail.get("town", "") or address_detail.get("village", ""),
                state=address_detail.get("state", ""),
                zip_code=address_detail.get("postcode", "") or address_detail.get("postal_code", ""),
                country=address_detail.get("country_code", ""),
                ISO_state=address_detail.get("ISO3166-2-lvl4", ""),
                lat=float(raw.get("lat", 0)),
                lon=float(raw.get("lon", 0)),
            )
        except (ValueError, TypeError) as e:
            logger.warning("failed to map api response to Address: %s", e)
            return None

# Address retriever Class
class AddressProcessor:
    # This helps apps to get address information
    # It can be called from a web page or from another service
    """
    The HTMX all is 
        @app.get("address/{postal_code}") and it will return the address information for the given postal code.
        @app get("address/latlong)
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        #slf.logger.level = logging.DEBUG
        self.logger.info("Initializing AddressProcessor")
        
        
        self.api_key       = settings.geocoding_api_key
        self._latest:      Optional[Address] = None

    def get_addressByPostalCode(self, address: Address) -> Optional[Address]:
        # Placeholder for geocoding API call
        # In a real implementation, this would call an external service
        # to convert the postal code into an address with lat/long.
        address_response = self._fetch_from_api(address)   
        if address_response is None:
            return None
        else:
            # insure we have a list
            address_l = [address_response] if isinstance(address_response, dict) else address_response
            
        self._latest = address_l
        return address_l
 
 # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    @staticmethod
    def quote_keep_plus(s, safe, encoding, errors):
        return quote(s, safe='+', encoding=encoding, errors=errors)
    

    def _fetch_from_api(self, a: Address) -> Optional[Address]:
        """
        based on the address components provided build up a location string to
        call the geocoding API. The API will return a list of possible matches. 
        Each component of the address can contain spaces but each segment has to connected with a '+'. 
        For example, if the street is "37032 Salmonberry St" and the city is "Sandy", the location string would be "37032 SalmonberrySt+Sandy".
        We will loop through the results to find the one that matches the postal code provided in the input address. 
        If we find a match, we will return that address. If we don't find a match, we will return None.
        """
        # Determine what address components you have and then construct the query accordingly
        location = ""
        if a.street:
            location = f"{a.street}"  #note future change to look for spaces in stree and city and replace with +
        if a.city and location:
            location += f"+{a.city}"
        elif a.city:
            location = f"{a.city}"
        if a.state and location:
            location += f"+{a.state}"
        elif a.state:
            location = f"{a.state}"
        if a.zip_code and location:
            location += f"+{a.zip_code}"
        elif a.zip_code:
            location = f"{a.zip_code}"
        if a.country and location:
            location += f"+{a.country}"
        elif a.country:
            location = f"{a.country}"   

        params = {"q": location, "api_key": self.api_key}
        
        address_url = urllib.parse.urlencode(params,quote_via=self.quote_keep_plus)
        address_url =  "https://geocode.maps.co/search?"+address_url
            
        with urllib.request.urlopen(address_url, timeout=10) as resp:
            address_data = json.loads(resp.read())
        self.logger.debug("Address data:%s ", address_data)
        if address_data == None:
            return None
        else:
            return address_data  # Calling function is responsible for determining how many results
        


if __name__ == "__main__":
    setup_logging()
    address_processor  = AddressProcessor()
    address = address_processor.get_addressByPostalCode(Address(street="37032 Salmonberry St", city="Sandy", state="", zip_code="", country="US"))
    print(f"address object is {type(address)}")
    print(f"address is {address}")
    for i in range(len(address)):
        # get the first address
        address_detail = Address.from_api_response(address[i])
        # get the key elemens in address detail
        '''house_number = address_detail.get("house_number", "")
        road = address_detail.get("road", "")
        city = address_detail.get("city", "") or address_detail.get("town", "") or address_detail.get("village", "")
        state = address_detail.get("state", "")
        postcode = address_detail.get("postcode", "") or address_detail.get("postal_code", "")
        country_code = address_detail.get("country_code", "")
        '''

        #print(f"address returned is {house_number} {road}, {city}, {state} {postcode}, {country_code}")
        print(f"address returned is {address_detail}")