from django.urls import path, re_path

from apps.blog import views

app_name = "blog"

urlpatterns = [
    path("list/", views.PostListView.as_view(), name="list-view"),
    re_path(
        r"(?P<slug>[-\w]+)/detail/", views.PostDetailView.as_view(), name="detail-view"
    ),
    re_path(
        r"(?P<slug>[-\w]+)/comment/form",
        views.CommentCreateView.as_view(),
        name="comment-form",
    ),
    re_path(
        r"(?P<pk>[-\w]+)/reply/form",
        views.CommentReplyCreateView.as_view(),
        name="comment-reply-form-view",
    ),
]
