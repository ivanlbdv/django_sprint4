from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm, ProfileEditForm
from .models import Category, Comment, Post, User


def get_posts(post_objects):
    """Получение постов из базы данных."""
    return post_objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now()
    ).annotate(comment_count=Count('comments'))


def get_paginator(request, items, num=10):
    """Получение объекта пагинации."""
    paginator = Paginator(items, num)
    num_pages = request.GET.get('page')
    return paginator.get_page(num_pages)


def index(request):
    """Главная страница."""
    template = 'blog/index.html'
    post_list = get_posts(Post.objects).order_by('-pub_date')
    page_obj = get_paginator(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница отдельной публикации."""
    template = 'blog/detail.html'
    posts = get_object_or_404(Post, id=post_id)
    if request.user != posts.author:
        posts = get_object_or_404(get_posts(Post.objects), id=post_id)
    comments = posts.comments.order_by('created_at')
    form = CommentForm()
    context = {'post': posts, 'form': form, 'comments': comments}
    return render(request, template, context)


def category_posts(request, category_slug):
    """Страница категории."""
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_posts(category.posts).order_by('-pub_date')
    page_obj = get_paginator(request, post_list)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)


@login_required
def create_post(request):
    """Создание поста."""
    template = 'blog/create.html'
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', request.user)
    else:
        form = PostForm()
    context = {'form': form}
    return render(request, template, context)


def profile(request, username):
    """Профиль пользователя."""
    template = 'blog/profile.html'
    user = get_object_or_404(User, username=username)
    posts_list = (
        user.posts
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    page_obj = get_paginator(request, posts_list)
    context = {'profile': user, 'page_obj': page_obj}
    return render(request, template, context)


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя."""
    template = 'blog/user.html'
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', request.user)
    else:
        form = ProfileEditForm(instance=request.user)
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    """Редактирование поста."""
    template = 'blog/create.html'
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        form = PostForm(
            request.POST, files=request.FILES or None, instance=post)
        if form.is_valid():
            post.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    """Удаление поста."""
    template = 'blog/create.html'
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        post.delete()
        return redirect('blog:index')
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        form = CommentForm(request.POST or None, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form, 'comment': comment}
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, template, context)
