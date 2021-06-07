from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    """Форма добавления поста"""
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']


class CommentForm(ModelForm):
    """Форма добавления комментария"""
    class Meta:
        model = Comment
        fields = ['text']
