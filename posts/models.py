from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=70, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    text = models.TextField(
        verbose_name="Текст публикации", help_text='Набирать текст тут'
    )
    group = models.ForeignKey(
        Group, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="posts", verbose_name="Группа",
        help_text='Укажите "Группу"'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField(
        verbose_name="Комментарий", help_text='Оставьте комментарий'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower",
        null=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following",
        null=True
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow'
        )]
