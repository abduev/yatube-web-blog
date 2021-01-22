import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Comment, Group, Post


USERNAME_1 = 'Smirnov'


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = get_user_model().objects.create(username=USERNAME_1)
        cls.post = Post.objects.create(
            author=cls.user,
            text='I\'m gonna be free',
            group=Group.objects.create(slug='cats')
        )
        cls.post_edit_url = reverse('post_edit', kwargs={
            'username': cls.user, 'post_id': cls.post.id
        })

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTest.user)

    def test_post_create(self):
        """Валидная форма создает пост. Работает редирект"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': 1,
            'text': 'Текст',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('post_new'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), post_count+1)
        post_created = Post.objects.filter(
            group=1, text='Текст', image='posts/small.gif'
        )
        self.assertTrue(post_created.exists())

    def test_post_edit(self):
        """При редактировании поста через форму на странице /<username>/edit
        изменяется соответствующая запись в БД и работает редирект"""
        post_count = Post.objects.count()
        form_data = {
            'group': 1,
            'text': 'Текст is edited'
        }
        response = self.authorized_client.post(
            PostCreateFormTest.post_edit_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            "post", kwargs={
                 'username': PostCreateFormTest.user,
                 'post_id': PostCreateFormTest.post.id
            }
        ))
        self.assertEqual(Post.objects.count(), post_count)
        post_is_edited = Post.objects.filter(group=1, text='Текст is edited')
        self.assertTrue(post_is_edited.exists())
