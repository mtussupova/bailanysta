from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone

def user_directory_path(instance, filename):
    return f"posts/{instance.author.username}/{filename}"


def avatar_upload_path(instance, filename):
    return f"avatars/{instance.user.username}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=160, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Profile({self.user.username})"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    body = models.TextField(max_length=500)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f"Post({self.author.username}, {self.created_at:%Y-%m-%d %H:%M})"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow'),
            models.CheckConstraint(check=~Q(follower=models.F('following')), name='no_self_follow'),
        ]


    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"Like({self.user.username}, post={self.post.id})"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment({self.user.username} → post={self.post.id})"