from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    """ Кастомизация модели Post в админке.
    Добавление инструментов поиска и фильтрации"""
    list_display = ("text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"
    list_per_page=10


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
