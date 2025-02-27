import uuid

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class SingletonMixin(models.Model):
    """An abstract base class that provides a Singleton pattern for models."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        self.pk = 1
        super().save(*args, **kwargs)
        self.set_cache()

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)

    def delete(self, *args, **kwargs):
        """Deleting an object on singleton pattern shouldn't be allowed, so we simply do nothing here."""
        pass

    def set_cache(self):
        cache.set(self.__class__.__name__, self)


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Timestampable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("تاریخ آخرین ویرایش")
    )

    class Meta:
        abstract = True


class LogicalDeletable(models.Model):
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(update_fields=["is_deleted"])

    def restore(self):
        self.is_deleted = False
        self.save(update_fields=["is_deleted"])


class Activable(models.Model):
    is_active = models.BooleanField(default=True, verbose_name=_("فعال؟"))

    class Meta:
        abstract = True

    def activate(self):
        self.is_active = True
        self.save(update_fields=["is_active"])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])


class Permalinkable(models.Model):
    slug = models.SlugField(unique=True, max_length=255)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.slug_source, allow_unicode=True)
        return super().save(*args, **kwargs)

    @property
    def slug_source(self):
        assert hasattr(self, "title"), (
            "Your model doesn't have a 'title' attribute. Either create a title attribute"
            "of type char or override `self.slug_source()` function"
        )
        return getattr(self, "title", "")


class Authorable(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="ایجاد کننده"
    )

    class Meta:
        abstract = True


class Sortable(models.Model):
    order = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        editable=True,
        db_index=True,
        verbose_name="ترتیب نمایش",
    )

    class Meta:
        abstract = True
