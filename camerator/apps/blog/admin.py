from django.contrib import admin

from apps.blog.models import Comment, CommentReply, Gallery, Post, PostCategory


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "created_date",
    )


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_date",
    )


@admin.register(Gallery)
class GalleyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "created_date",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "body", "post", "created_date", "active")
    list_filter = ("active", "created_date")
    search_fields = ("name", "email", "body")
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


@admin.register(CommentReply)
class CommentReplyAdmin(admin.ModelAdmin):
    list_display = ("comment", "body", "created_date")
