from django.test import TestCase
from apps.blog.models import Post, PostCategory, Gallery, Comment, CommentReply
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()


class TestPostModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.post_category = PostCategory.objects.create(title="Test Category")
        self.gallery = Gallery.objects.create(
            title="Test Gallery", description="Test Description"
        )

    def test_post_model(self):
        post = Post.objects.create(
            title="Test Post",
            author=self.user,
            gallery=self.gallery,
            slug="test-post",
            image="test_image.jpg",
            publish_date=now(),
            status=Post.PostChoices.PUBLISHED,
            caption="Test Caption",
        )
        post.category.add(self.post_category)
        self.assertEqual(str(post), "Test Post")
        self.assertEqual(list(post.category.all()), [self.post_category])
        self.assertEqual(post.gallery, self.gallery)
        self.assertEqual(post.status, Post.PostChoices.PUBLISHED)
        self.assertEqual(post.caption, "Test Caption")


class TestPostCategoryModel(TestCase):
    def setUp(self):
        self.post_category = PostCategory.objects.create(title="Test Category")

    def test_post_category_model(self):
        self.assertEqual(str(self.post_category), "Test Category")


class TestPostGalleryModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.post_category = PostCategory.objects.create(title="Test Category")
        self.gallery = Gallery.objects.create(
            title="Test Gallery", description="Test Description"
        )
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user,
            gallery=self.gallery,
            slug="test-post",
            image="test_image.jpg",
            publish_date=now(),
            status=Post.PostChoices.PUBLISHED,
            caption="Test Caption",
        )
        self.post.category.add(self.post_category)

    def test_post_gallery_model(self):
        post_gallery = Gallery.objects.create(
            title="Test Gallery",
            description="Test Description",
        )
        self.assertEqual(post_gallery.title, "Test Gallery")
        self.assertEqual(post_gallery.description, "Test Description")


class TestCommentModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.gallery = Gallery.objects.create(
            title="Test Gallery", description="Test Description"
        )
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user,
            gallery=self.gallery,
            slug="test-post",
            image="test_image.jpg",
            publish_date=now(),
            status=Post.PostChoices.PUBLISHED,
            caption="Test Caption",
        )

    def test_comment_model(self):
        comment = Comment.objects.create(
            post=self.post,
            name="Test User",
            email="test@example.com",
            body="Test Comment",
        )
        self.assertEqual(str(comment), "Comment Test Comment by Test User")
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.name, "Test User")
        self.assertEqual(comment.email, "test@example.com")
        self.assertEqual(comment.body, "Test Comment")


class TestCommentReplyModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.gallery = Gallery.objects.create(
            title="Test Gallery", description="Test Description"
        )
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user,
            gallery=self.gallery,
            slug="test-post",
            image="test_image.jpg",
            publish_date=now(),
            status=Post.PostChoices.PUBLISHED,
            caption="Test Caption",
        )
        self.comment = Comment.objects.create(
            post=self.post,
            name="Test User",
            email="test@example.com",
            body="Test Comment",
        )

    def test_comment_reply_model(self):
        comment_reply = CommentReply.objects.create(
            comment=self.comment, body="Test Reply"
        )
        self.assertEqual(comment_reply.comment, self.comment)
        self.assertEqual(comment_reply.body, "Test Reply")
