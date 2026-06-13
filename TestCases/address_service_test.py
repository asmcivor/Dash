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
        add = Address("", "", "", "97055", "US")
        address = address_processor.get_addressByPostalCode(add)
        self.assertEqual(len(address), 1)
        address_detail = Address.from_api_response(address[0])
        self.assertEqual(address_detail.house_number, "")
        self.assertEqual(address_detail.street, "") 
        self.assertEqual(address_detail.city, "Sandy")
        self.assertEqual(address_detail.state, "Oregon")

    def test_address_bad_zip_code(self):
        address_processor  = AddressProcessor()
        add = Address("", "", "", "00000", "US")
        pytest.mark.xfail(raises=NotImplementedError, reason="Waiting for implementation")
        ##address = address_processor.get_addressByPostalCode(add)
        ##self.assertIsNone(address)
    


if __name__ == "__main__":
    unittest.main()