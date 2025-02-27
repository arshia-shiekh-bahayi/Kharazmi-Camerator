from django import forms

from apps.blog.models import Comment, CommentReply


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("name", "email", "body")


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentReply
        fields = ("body",)
