import unittest
import pytest 
import logging
from services.address_service import Address, AddressProcessor


def setup_logging():
    logger = logging.getLogger()
    #logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

class TestAddress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_logging()

    def setUp(self):
        self.service = AddressProcessor()

    def test_address_initialization(self):
        address_processor  = AddressProcessor()
        add = Address("", "", "", "97055", "US")
        address = address_processor.get_addressByPostalCode(add)
        # should return a list with 1 item
        self.assertEqual(len(address), 1)
        address_detail = address[0].get("address", {})
        self.assertEqual(address_detail.get("house_number", " "), " ")
        self.assertEqual(address_detail.get("road", " "), " ")
        city = address_detail.get("city", "") or address_detail.get("town", "") or address_detail.get("village", "")
        self.assertEqual(city, "Sandy")
        self.assertEqual(address_detail.get("state", " "), "Oregon")
        self.assertEqual(address_detail.get("postcode", " "), "97055")
        self.assertEqual(address_detail.get("country_code", " "), "us")
        self.assertAlmostEqual(float(address[0].get("lat", 0)), 45.394, places=2)  
        self.assertAlmostEqual(float(address[0].get("lon", 0)), -122.257, places=2)

    def test_address_by_fullAddress_construct(self):
        address_processor  = AddressProcessor()
        address = address_processor.get_addressByPostalCode(Address(street="37032 Salmonberry St", city="Sandy", state="OR", zip_code="97055", country="US"))
        # should return a full address for 1 location
        self.assertEqual(len(address), 1)
        address_detail = address[0].get("address",{})
        # get the key elemens in address detail
        house_number = address_detail.get("house_number", "")
        road = address_detail.get("road", "")
        city = address_detail.get("city", "") or address_detail.get("town", "") or address_detail.get("village", "")
        state = address_detail.get("state", "")
        postcode = address_detail.get("postcode", "") or address_detail.get("postal_code", "")
        country_code = address_detail.get("country_code", "")
        ISO_state = address_detail.get("ISO3166-2-lvl4", "")

        self.assertEqual(house_number, "37032")
        self.assertEqual(road, "Salmonberry Street")
        self.assertEqual(city, "Sandy")
        self.assertEqual(state, "Oregon")
        self.assertEqual(postcode, "97055")
        self.assertEqual(country_code, "us")
        self.assertEqual(ISO_state, 'US-OR') 
        self.assertAlmostEqual(float(address[0].get("lat", 0)), 45.412, places=2)  
        self.assertAlmostEqual(float(address[0].get("lon", 0)), -122.280, places=2)
        

    def test_address_by_zip_code(self):
        address_processor  = AddressProcessor()
        add = Address("", "", "", "97055", "US")
        address = address_processor.get_addressByPostalCode(add)
        self.assertEqual(len(address), 1)
        address_detail = address[0].get("address",{})
        # get the key elemens in address detail
        house_number = address_detail.get("house_number", "")
        road = address_detail.get("road", "")
        city = address_detail.get("city", "") or address_detail.get("town", "") or address_detail.get("village", "")
        state = address_detail.get("state", "")
        postcode = address_detail.get("postcode", "") or address_detail.get("postal_code", "")
        country_code = address_detail.get("country_code", "")
        ISO_state = address_detail.get("ISO3166-2-lvl4", "")
        self.assertEqual(house_number, "")
        self.assertEqual(road, "") 
        self.assertEqual(city, "Sandy")
        self.assertEqual(state, "Oregon")

    def test_address_bad_zip_code(self):
        address_processor  = AddressProcessor()
        add = Address("", "", "", "00000", "US")
        pytest.mark.xfail(raises=NotImplementedError, reason="Waiting for implementation")
        ##address = address_processor.get_addressByPostalCode(add)
        ##self.assertIsNone(address)
    


if __name__ == "__main__":
    unittest.main()