from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_page_uses_correct_template(self):
        """При запросе к странице об авторе
        применяется нужный шаблон"""
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_page_uses_correct_template(self):
        """При запросе к странице о технологиях
        применяется нужный шаблон"""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
