from django.contrib import auth
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


INDEX_URL = reverse('index')
USERNAME_1 = 'Smirnov'


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username=USERNAME_1)
        posts = []
        for i in range(1, 14):
            posts.append(Post(
                text='test',
                author=cls.user,
            ))
        Post.objects.bulk_create(posts, 14)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        """На главную страницу передаётся
        не более установленного количества постов"""
        response = self.guest_client.get(INDEX_URL)
        page_1 = response.context.get('paginator').get_page(1)
        self.assertEqual(page_1.object_list.count(), 10)

    def test_second_page_containse_three_records(self):
        """На вторую страницу передается
        оставшееся количество постов"""
        response = self.guest_client.get(INDEX_URL + '?page=2')
        page_2 = response.context.get('paginator').get_page(2)
        self.assertEqual(page_2.object_list.count(), 3)
