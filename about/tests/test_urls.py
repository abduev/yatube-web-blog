from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_accessible_by_name(self):
        """Статичные страницы author, technology доступны"""
        pages_locations = ['/about/author/', '/about/tech/']
        for loc in pages_locations:
            with self.subTest(loc=loc):
                response = self.guest_client.get(loc)
                self.assertEqual(response.status_code, 200)

    def test_pages_url_uses_correct_template(self):
        """URL-адреса(статичные) использует соответствующий шаблоны."""
        template_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, url in template_url_names.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
