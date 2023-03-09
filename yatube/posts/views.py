from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm

POSTS_LIMIT: int = 10


def get_paginator(request, posts, posts_per_page):
    """Get page_obj via paginator."""
    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def index(request):
    """Main page."""
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = get_paginator(request, posts, POSTS_LIMIT)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Group posts page."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts_group.select_related('author').all()
    page_obj = get_paginator(request, posts, POSTS_LIMIT)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Profile page."""
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related('group').all()
    page_obj = get_paginator(request, posts, POSTS_LIMIT)

    context = {
        'author': user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Single post page."""
    post = get_object_or_404(Post.objects.select_related('group', 'author'),
                             pk=post_id)

    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Create a post."""
    is_edit = False
    form = PostForm(request.POST or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', post.author.username)

    context = {
        'form': form,
        'is_edit': is_edit,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Edit the post."""
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': is_edit,
    }

    return render(request, 'posts/create_post.html', context)
