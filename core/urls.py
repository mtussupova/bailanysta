from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_view, name='feed'),

    path('auth/signup/', views.signup_view, name='signup'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    path('post/create/', views.create_post_view, name='create_post'),
    path('post/<int:post_id>/like/', views.toggle_like_view, name='toggle_like'),
    path('post/<int:post_id>/comment/', views.add_comment_view, name='add_comment'),

    path('u/<str:username>/', views.profile_view, name='profile'),
    path('u/<str:username>/follow/', views.toggle_follow_view, name='toggle_follow'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
]