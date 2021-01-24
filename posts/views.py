from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related(
        'author', 'group'
    ).prefetch_related(
        'comments__author'
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {
        "page": page, "paginator": paginator
    },)


def group_posts(request, slug):
    group = get_object_or_404(
        Group.objects.all(
        ).prefetch_related(
            'posts__author', 'posts__comments'
        ),
        slug=slug
    )
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {
        "group": group, "page": page, "paginator": paginator
    },)


@login_required
def post_new(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect("index")
    return render(request, "post_new.html", {"form": form})


def is_subscribed(user, author):
    if user.is_authenticated:
        return Follow.objects.filter(
            user=user, author=author).exists()
    

def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all().prefetch_related('comments__author', 'group')
    following = is_subscribed(request.user, author)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        "page": page, "author": author,
        "paginator": paginator, "following": following
        })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    post_count = author.posts.all().count()
    comments = Comment.objects.filter(
        post__id=post_id
    ).select_related('author')
    form = CommentForm(request.POST or None)
    return render(request, 'post.html', {
            "post": post, "post_count": post_count, "author": author,
            "comments": comments, "form": form
        })


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user.username == post.author.username:
        form = PostForm(
            request.POST or None, files=request.FILES or None, instance=post
        )
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect("post", username=username, post_id=post_id)
        return render(request, "post_edit.html", {
            "form": form, "post": post
        })
    return redirect("post", username=username, post_id=post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "comments.html", {"form": form, "post": post})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user
    ).select_related(
        'author', 'group'
    ).prefetch_related(
        'comments__author'
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
        "page": page, "paginator": paginator
    },)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if (request.user != author and not is_subscribed(request.user, author)):
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author__username=username
        ).delete()
    return redirect("profile", username=username)
