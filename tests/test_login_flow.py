import unittest
from app import app

class TestLoginFlow(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_redirect(self):
        """Test that /login redirects to /login_page"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login_page' in response.location)

    def test_login_page_load(self):
        """Test that /login_page loads correctly"""
        response = self.app.get('/login_page')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Continuar al Dashboard', response.data)

if __name__ == '__main__':
    unittest.main()
