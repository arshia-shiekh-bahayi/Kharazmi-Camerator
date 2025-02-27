from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from apps.blog.forms import CommentForm, CommentReplyForm
from apps.blog.models import Comment, Post, PostCategory


class PostListView(ListView):
    template_name = "blog/post-list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        queryset = Post.objects.filter(status=Post.PostChoices.PUBLISHED)
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get("category"):
            queryset = queryset.filter(category__id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = PostCategory.objects.all()
        return context


class PostDetailView(DetailView):
    model = Post
    slug_field = "slug"
    template_name = "blog/post-detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(post=context["post"])
        return context


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment-form.html"

    def form_valid(self, form):
        post = get_object_or_404(Post, slug=self.kwargs["slug"])
        form.instance.post = post
        messages.success(self.request, "Your commment has been submited successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Your comment couldn't be submitted. Please try again."
        )
        return super().form_invalid(form)

    def get_success_url(self):
        success_url = reverse("blog:detail-view", kwargs={"slug": self.kwargs["slug"]})
        return success_url


class CommentReplyCreateView(CreateView):
    model = CommentReplyForm
    form_class = CommentReplyForm
    template_name = "blog/comment-reply-form.html"

    def form_valid(self, form):
        comment = get_object_or_404(Comment, id=self.kwargs["pk"])
        form.instance.comment = comment
        messages.success(self.request, "Your reply has been submited successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Your reply has not been submited successfully")
        return super().form_invalid(form)

    def get_success_url(self):
        comment = get_object_or_404(Comment, id=self.kwargs["pk"])
        post_slug = comment.post.slug
        success_url = reverse("blog:detail-view", kwargs={"slug": post_slug})
        return success_url
