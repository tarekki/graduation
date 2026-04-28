from django.db import models


class Role(models.Model):
    """System role; referenced by User.role_id. Use `code` in permission checks."""

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.name} ({self.code})"


class CarBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class CarColor(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
