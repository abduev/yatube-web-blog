from django.contrib.auth import get_user_model
from django.db.models.deletion import SET_NULL
from django.test import TestCase

from posts.models import Group, Post


USERNAME_1 = 'Smirnov'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test'
        )
        cls.post = Post.objects.create(
            author=get_user_model().objects.create(username=USERNAME_1),
            text='Текст публикации',
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'group': 'Группа',
            'text': 'Текст публикации'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_meta = post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_meta, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'group': 'Укажите "Группу"',
            'text': 'Набирать текст тут'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                help_text_meta = post._meta.get_field(value).help_text
                self.assertEqual(help_text_meta, expected)

    def test_post_string_representation(self):
        """В модели Post значение поля __str__ отображается правильно"""
        post = PostModelTest.post
        expected_name = post.text[:15]
        self.assertEqual(expected_name, str(post))

    def test_group_string_representation(self):
        """В модели Group значение поля __str__ отображается правильно"""
        group = PostModelTest.group
        expected_name = group.title
        self.assertEqual(expected_name, str(group))
