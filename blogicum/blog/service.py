from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Count

from .constants import POSTS_PER_PAGE


def get_posts(post_objects, is_count_comments=True):
    """Получение постов из базы данных."""
    posts_query = post_objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now()
    ).order_by(
        '-pub_date'
    )
    return posts_query.annotate(
        comment_count=Count('comments')
    ) if is_count_comments else posts_query


def get_paginator(request, items, num=POSTS_PER_PAGE):
    """Получение объекта пагинации."""
    paginator = Paginator(items, num)
    num_pages = request.GET.get('page')
    return paginator.get_page(num_pages)
