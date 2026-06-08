from django.db import models


class Role(models.Model):
    """System role; referenced by User.role_id. Use `code` in permission checks.

    `name` holds the default (English) label; `name_ar` is the optional Arabic
    label. APIs resolve which one to return from the request locale, falling
    back to `name` when the Arabic value is empty.
    """

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=64)
    name_ar = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.name} ({self.code})"


class CarBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class CarColor(models.Model):
    name = models.CharField(max_length=64, unique=True)
    name_ar = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
