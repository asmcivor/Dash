from re import match
import unittest
from unittest import case
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


    def test_address_by_fullAddress_construct(self):
        address_processor  = AddressProcessor()
        address = address_processor.get_addressByPostalCode(Address(street="37032 Salmonberry St", city="Sandy", state="OR", zip_code="97055", country="US"))
        # should return a full address for 1 location
        self.assertEqual(len(address), 1)
        # populate the address record from the first response
        address_detail = Address.from_api_response(address[0])

        self.assertEqual(address_detail.house_number, "37032")
        self.assertEqual(address_detail.street, "Salmonberry Street")
        self.assertEqual(address_detail.city, "Sandy")
        self.assertEqual(address_detail.state, "Oregon")
        self.assertEqual(address_detail.zip_code, "97055")
        self.assertEqual(address_detail.country, "us")
        self.assertEqual(address_detail.ISO_state, 'US-OR') 
        self.assertAlmostEqual(address_detail.lat, 45.412, places=2)  
        self.assertAlmostEqual(address_detail.lon, -122.280, places=2)
        

    def test_address_by_zip_code(self):
        address_processor  = AddressProcessor()
        add = Address(street="", city="", state="", zip_code="97055", country="US")
        address = address_processor.get_addressByPostalCode(add)
        self.assertEqual(len(address), 1)
        address_detail = Address.from_api_response(address[0])
        self.assertEqual(address_detail.house_number, "")
        self.assertEqual(address_detail.street, "") 
        self.assertEqual(address_detail.city, "Sandy")
        self.assertEqual(address_detail.state, "Oregon")

    def test_multiple_responses(self):
        address_processor  = AddressProcessor()
        add = Address(street="", city="Sandy", state="", zip_code="", country="US")
        addressresponse = address_processor.get_addressByPostalCode(add)
        self.assertEqual(len(addressresponse), 8)
        for i, addr in enumerate(addressresponse):
            address_detail = Address.from_api_response(addr)
            match i:
                case 0:
                    self.assertEqual(address_detail.state, "Utah")
                case 1:
                    self.assertEqual(address_detail.state, "Oregon")
                case 2|3:
                    self.assertEqual(address_detail.state, "Pennsylvania")
                case 4|5:
                    self.assertEqual(address_detail.state, "West Virginia")
                case 6:
                    self.assertEqual(address_detail.state, "Florida")
                case 7:
                    self.assertEqual(address_detail.state, "Georgia")

    def test_address_bad_zip_code(self):
        address_processor  = AddressProcessor()
        add = Address("", "", "", "00000", "US")
        pytest.mark.xfail(raises=NotImplementedError, reason="Waiting for implementation")
        ##address = address_processor.get_addressByPostalCode(add)
        ##self.assertIsNone(address)
    


if __name__ == "__main__":
    unittest.main()