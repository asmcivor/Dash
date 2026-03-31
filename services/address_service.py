from __future__ import annotations

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
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    lat: float | None = None
    long: float | None = None  

# Address retriever Class
class AddressProcessor:
    # This helps apps to get address information
    # It can be called from a web page or from another service
    """
    The HTMX all is 
        @app.get("address/{postal_code}") and it will return the address information for the given postal code.
        @app get("address/latlong)
    """
    def __init__(self, api_key: str = "") -> None:
        self.logger = logging.getLogger(__name__)
        #slf.logger.level = logging.DEBUG
        self.logger.info("Initializing AddressProcessor")
        
        
        self.api_key       = "69b891701591a586791541rza1a4f06"
        self._latest:      Optional[Address] = None

    def get_addressByPostalCode(self, address: Address) -> Optional[Address]:
        # Placeholder for geocoding API call
        # In a real implementation, this would call an external service
        # to convert the postal code into an address with lat/long.
        address = self._fetch_from_api(address)   
        if address is None:
            return None
        self._latest = address
        return address
 
 # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    @staticmethod
    def quote_keep_plus(s, safe, encoding, errors):
        return quote(s, safe='+', encoding=encoding, errors=errors)
    

    
    def _fetch_from_api(self, a: Address) -> Address:
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
        for i in range(len(address_data)):
            self.logger.debug("i: %d, postcode: %s", i, address_data[i].get("address",{}).get("postcode", ""))
            if address_data[i].get("address",{}).get("postcode", "") == a.zip_code:
                self.logger.debug("Found matching postal code: %s at index %d", location, i)
                break
        else:
            self.logger.debug("No matching postal code found for: %s", location)
            return None 
        result = address_data[i]  # take the ith result
        self.logger.debug("Final result: %s", result)
        return Address(
            lat=float(result.get("lat", "")),    
            long=float(result.get("lon", "")),
            street=result.get("address",{}).get("house_number", "") + " " + result.get("address", {}).get("road", ""),
            city=result.get("address", {}).get("town", ""),
            state=result.get("address", {}).get("state", ""), 
            zip_code=result.get("address", {}).get("postcode", ""),
            country=result.get("address", {}).get("country_code", "")
        )


if __name__ == "__main__":
    setup_logging()
    add = Address("37032 Salmonberry St", "Sandy", "OR", "97055", "US")
    processor = AddressProcessor()
    address = processor.get_addressByPostalCode(add) 
    print(address)
    add2 = Address("", "", "", "97055", "US")
    print(f"address is {add2.street} before setting zip code and country") 
    address2 = processor.get_addressByPostalCode(add2) 
    print(f"address2 is {address2}")
    #address = processor.get_addressByPostalCode("97055", "US")
    #print(address)
    #address = processor.get_addressByPostalCode("00000", "US")
    #print(address)
