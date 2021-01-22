import shutil
import tempfile

from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post


USERNAME_1 = 'Smirnov'
SLUG = 'leo'
POST_EDIT_URL = reverse('post_edit',
                        kwargs={'username': USERNAME_1, 'post_id': 1})
INDEX_URL = reverse('index')
POST_NEW_URL = reverse('post_new')
GROUP_URL = reverse('group_posts',
                    kwargs={'slug': SLUG})
GROUP_WRONG_URL = reverse('group_posts', kwargs={'slug': 'cats'})
PROFILE_URL = reverse('profile',
                      kwargs={'username': USERNAME_1})


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = get_user_model().objects.create_user(username=USERNAME_1)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug=SLUG
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': INDEX_URL,
            'post_new.html': POST_NEW_URL,
            'group.html': GROUP_URL
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        expected_post = PostViewsTests.post
        actual_post = response.context.get('page')[0]
        self.assertEqual(actual_post, expected_post)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_URL)
        expected_post = PostViewsTests.group
        actual_post = response.context.get('group')
        self.assertEqual(actual_post, expected_post)

    def test_profile_show_correct_context(self):
        """Шаблон профайла пользователя сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        expected_post = PostViewsTests.post
        actual_post = response.context.get('page')[0]
        self.assertEqual(actual_post, expected_post)

    def test_post_show_correct_context(self):
        """Шаблон отдельного поста пользователя сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(POST_EDIT_URL)
        expected_post = PostViewsTests.post
        actual_post = response.context.get('post')
        self.assertEqual(actual_post, expected_post)

    def test_newpost_page_show_correct_context(self):
        """Шаблон post_new сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_NEW_URL)
        form_fields = {
            'group': forms.ChoiceField,
            'text': forms.CharField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_postedit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_EDIT_URL)
        form_fields = {
            'group': forms.ChoiceField,
            'text': forms.CharField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_appear_in_homepage(self):
        """Пост появился на главной странице"""
        response = self.authorized_client.get(INDEX_URL)
        self.assertContains(response, PostViewsTests.post)

    def test_post_appear_in_group(self):
        """Пост появился на странице выбранной группы"""
        response = self.authorized_client.get(GROUP_URL)
        self.assertContains(response, PostViewsTests.post)

    def test_post_appear_in_wrong_group(self):
        """Пост не попал в группу, для которой не был предназначен."""
        self.group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='cats'
        )
        response = self.authorized_client.get(GROUP_WRONG_URL)
        self.assertNotContains(response, PostViewsTests.post)

    def test_cash_function_in_homepage(self):
        """Кэширование страницы index работает исправно."""
        response_1 = self.authorized_client.get(INDEX_URL)
        Post.objects.create(
            author=PostViewsTests.user,
            text='Текст new',
            group=PostViewsTests.group,
            image=PostViewsTests.uploaded
        )
        response_2 = self.authorized_client.get(INDEX_URL)
        self.assertHTMLEqual(str(response_1.content), str(response_2.content))
