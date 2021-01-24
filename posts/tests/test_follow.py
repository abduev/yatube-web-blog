import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Follow, Comment


USERNAME_1 = 'Smirnov'
USERNAME_2 = 'Ivanov'
INDEX_URL = reverse('index')
FOLLOW_INDEX_URL = reverse('follow_index')


class PostFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user_author = get_user_model().objects.create_user(
            username=USERNAME_1
        )
        cls.user_subscriber = get_user_model().objects.create_user(
            username=USERNAME_2
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Текст',
        )
        cls.post_comments_url = reverse('add_comment', kwargs={
            'username': cls.user_author, 'post_id': cls.post.id
        })

        cls.follow = Follow.objects.create(
            user=cls.user_subscriber,
            author=cls.user_author
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.client_author = Client()
        self.client_subscriber = Client()
        self.client_author.force_login(PostFollowTests.user_author)
        self.client_subscriber.force_login(PostFollowTests.user_subscriber)

    def test_user_subcribes_and_to_author(self):
        """Авторизованный пользователь успешно подписался на автора"""
        is_subscribed = Follow.objects.filter(
            user=PostFollowTests.user_subscriber,
            author=PostFollowTests.user_author
        )
        self.assertTrue(is_subscribed.exists())

    def test_user_unsubcribes_to_author(self):
        """Авторизованный пользователь успешно отписался от автора"""
        PostFollowTests.follow.delete()
        is_subscribed = Follow.objects.filter(
            user=PostFollowTests.user_subscriber,
            author=PostFollowTests.user_author
        )
        self.assertFalse(is_subscribed.exists())

    def test_author_post_appear_in_user_subscribe(self):
        """Новая запись пользователя появляется в ленте тех,
         кто на него подписан"""
        response = self.client_subscriber.get(FOLLOW_INDEX_URL)
        self.assertContains(response, PostFollowTests.post)

    def test_author_post_doesnt_appear_in_user_subscribe(self):
        """Новая запись пользователя не появляется в ленте тех,
         кто на него не подписан"""
        response = self.client_author.get(FOLLOW_INDEX_URL)
        self.assertNotContains(response, PostFollowTests.post)

    def test_authorized_user_is_allowed_to_comment_post(self):
        """Авторизованный пользователь может комментировать пост"""
        form_data = {
            'author': PostFollowTests.user_subscriber,
            'post': PostFollowTests.post,
            'text': 'Текст комментария'
        }
        response = self.client_subscriber.post(
            PostFollowTests.post_comments_url,
            data=form_data,
            follow=True
        )
        post_is_commented = Comment.objects.filter(
            author=PostFollowTests.user_subscriber,
            post=PostFollowTests.post,
            text='Текст комментария'
        )
        self.assertTrue(post_is_commented.exists())
        self.assertRedirects(response, reverse(
            "post", kwargs={
                 'username': PostFollowTests.user_author,
                 'post_id': PostFollowTests.post.id
            }
        ))

    def test_not_authorized_user_is_allowed_to_comment_post(self):
        """Неавторизованный пользователь не может комментировать пост(
            перенаправление на форму авторизации)"""
        response = self.guest_client.get(PostFollowTests.post_comments_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?next=/Smirnov/1/comment')
