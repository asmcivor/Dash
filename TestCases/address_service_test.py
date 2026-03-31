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
        self.assertEqual(address.street, " ")
        self.assertEqual(address.city, "Sandy")
        self.assertEqual(address.state, "Oregon")
        self.assertEqual(address.zip_code, "97055")
        self.assertEqual(address.country, "us")
        self.assertAlmostEqual(address.lat, 45.394, places=2)  
        self.assertAlmostEqual(address.long, -122.257, places=2)
    
    def test_address_by_fullAddress_construct(self):
        address_processor  = AddressProcessor()
        address = address_processor.get_addressByPostalCode(Address(street="37032 Salmonberry St", city="Sandy", state="OR", zip_code="97055", country="US"))
        self.assertEqual(address.street, "37032 Salmonberry Street")
        self.assertEqual(address.city, "Sandy")
        self.assertEqual(address.state, "Oregon")
        self.assertEqual(address.zip_code, "97055")
        self.assertEqual(address.country, "us")
        self.assertAlmostEqual(address.lat, 45.412, places=2)  
        self.assertAlmostEqual(address.long, -122.280, places=2)
    def test_address_by_fullAddress(self):
        address_processor  = AddressProcessor()
        add = Address("37032 Salmonberry St", "Sandy", "OR", "97055", "US")
        address = address_processor.get_addressByPostalCode(add)
        self.assertEqual(address.street, "37032 Salmonberry Street")
        self.assertEqual(address.city, "Sandy")
        self.assertEqual(address.state, "Oregon")
        self.assertEqual(address.zip_code, "97055")
        self.assertEqual(address.country, "us")
        self.assertAlmostEqual(address.lat, 45.412, places=2)  
        self.assertAlmostEqual(address.long, -122.280, places=2)

    def test_address_by_zip_code(self):
        address_processor  = AddressProcessor()
        add = Address("", "", "", "97055", "US")
        address = address_processor.get_addressByPostalCode(add)
        self.assertEqual(address.city, "Sandy")
        self.assertEqual(address.state, "Oregon")

    def test_address_bad_zip_code(self):
        address_processor  = AddressProcessor()
        add = Address("", "", "", "00000", "US")
        address = address_processor.get_addressByPostalCode(add)
        self.assertIsNone(address)

if __name__ == "__main__":
    unittest.main()