from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post


INDEX_LOC = '/'
GROUP_LOC = '/group/cats/'
PROFILE_LOC = '/Smirnov/'
POST_LOC = '/Smirnov/1/'
EDIT_LOC = '/Smirnov/1/edit/'
NOT_EXIST_LOC = '/notexistpage/'
POST_NEW_LOC = '/new/'
USERNAME_1 = 'Smirnov'
USERNAME_2 = 'Ivanov'


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = get_user_model().objects.create(username=USERNAME_1)
        cls.user_2 = get_user_model().objects.create(username=USERNAME_2)
        Post.objects.create(
            author=cls.user_1,
            text='I\'m gonna be free',
            group=Group.objects.create(slug='cats')
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_1 = Client()
        self.authorized_client_2 = Client()
        self.authorized_client_1.force_login(PostURLTests.user_1)
        self.authorized_client_2.force_login(PostURLTests.user_2)

    def test_pages_anonymous_accessible(self):
        """Страницы доступны неавторизованному пользователю"""
        pages_locations = [INDEX_LOC, GROUP_LOC, PROFILE_LOC, POST_LOC]
        for loc in pages_locations:
            with self.subTest(loc=loc):
                response = self.guest_client.get(loc)
                self.assertEqual(response.status_code, 200)

    def test_pages_authorized_accessible(self):
        """Страницы доступны авторизованному пользователю"""
        pages_locations = [
            INDEX_LOC, GROUP_LOC, POST_NEW_LOC, PROFILE_LOC,
            POST_LOC, EDIT_LOC
        ]
        for loc in pages_locations:
            with self.subTest(loc=loc):
                response = self.authorized_client_1.get(loc)
                self.assertEqual(response.status_code, 200)

    def test_pages_anonymous_redirect(self):
        """Страницы создания и редактирования поста
        перенаправляют неавторизованного пользователя"""
        pages_locations = [POST_NEW_LOC, EDIT_LOC]
        for loc in pages_locations:
            with self.subTest(loc=loc):
                response = self.guest_client.get(loc)
                self.assertEqual(response.status_code, 302)

    def test_pages_authorized_redirect(self):
        """Страница редактирования поста
        перенаправляет не автора поста"""
        pages_locations = [EDIT_LOC]
        for loc in pages_locations:
            with self.subTest(loc=loc):
                response = self.authorized_client_2.get(loc)
                self.assertRedirects(response, POST_LOC,
                                     status_code=302)

    def test_urls_uses_correct_template(self):
        """URL-адреса использует соответствующий шаблоны."""
        template_url_names = {
            'index.html': INDEX_LOC,
            'group.html': GROUP_LOC,
            'post_new.html': POST_NEW_LOC,
            'profile.html': PROFILE_LOC,
            'post.html': POST_LOC,
            'post_edit.html': EDIT_LOC
        }
        for template, url in template_url_names.items():
            with self.subTest():
                response = self.authorized_client_1.get(url)
                self.assertTemplateUsed(response, template)

    def test_code_404_returns(self):
        """Cервер возвращает код 404, если страница не найдена."""
        response = self.authorized_client_1.get(NOT_EXIST_LOC)
        self.assertEqual(response.status_code, 404)
