from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

User = get_user_model()


class PostCategory(models.Model):
    title = models.CharField(max_length=200, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Gallery(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    class PostChoices(models.TextChoices):
        PUBLISHED = "published"
        DRAFT = "draft"

    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    gallery = models.ForeignKey(
        Gallery, related_name="images", on_delete=models.CASCADE, null=True
    )
    slug = models.SlugField(allow_unicode=True)
    image = models.ImageField(upload_to="posts/images/", blank=False, null=False)
    category = models.ManyToManyField(PostCategory, blank=False, related_name="posts")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(default=now, blank=True, null=True)
    status = models.CharField(choices=PostChoices.choices, default="draft")
    caption = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_date"]
        app_label = "blog"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_date"]

    def __str__(self):
        return f"Comment {self.body} by {self.name}"


class CommentReply(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="replies"
    )
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
