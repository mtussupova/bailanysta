from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import SignUpForm, PostForm, CommentForm, ProfileForm
from .models import Post, Follow, Like, Comment, Profile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Аккаунт создан! Войдите, чтобы продолжить.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('feed')
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def feed_view(request):
    # Посты от вас и тех, на кого вы подписаны
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    posts = Post.objects.filter(author__in=list(following_ids) + [request.user.id]).annotate(num_likes=Count('likes'))

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'feed.html', {
        'page_obj': page_obj,
        'post_form': PostForm(),
        'comment_form': CommentForm(),
    })


@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост опубликован!')
    return redirect('feed')


@login_required
def toggle_like_view(request, post_id):
    if request.method != 'POST':
        return HttpResponseForbidden()
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def add_comment_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.user = request.user
            c.post = post
            c.save()
    return redirect('feed')


@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    posts = user.posts.all()

    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    return render(request, 'profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'profile_form': ProfileForm(instance=profile) if request.user == user else None,
    })


@login_required
def toggle_follow_view(request, username):
    if request.method != 'POST':
        return HttpResponseForbidden()
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, 'Нельзя подписаться на себя.')
        return redirect('profile', username=username)

    obj, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        obj.delete()
    return redirect('profile', username=username)


@login_required
def update_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
    return redirect('profile', username=request.user.username)