import unittest
from application import application

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.application = application.test_client()

    def test_basic_functionality(self):
        self.assertEqual(1 + 1, 2)

    def test_home_page(self):
        response = self.application.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()