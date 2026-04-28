from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        fn = (first_name or "").strip()
        ln = (last_name or "").strip()
        if not fn:
            raise ValueError("First name is required.")
        if not ln:
            raise ValueError("Last name is required.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=fn[:75],
            last_name=ln[:75],
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        Role = apps.get_model("lookups", "Role")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if "role" not in extra_fields and "role_id" not in extra_fields:
            extra_fields["role"] = Role.objects.get(code="ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(
        "lookups.Role",
        on_delete=models.PROTECT,
        related_name="users",
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_full_name(self):
        """Django convention (admin, templates); not stored in DB."""
        return self.full_name

    def get_short_name(self):
        """Django convention for greetings / short labels."""
        return self.first_name

    def __str__(self):
        return f"{self.full_name} <{self.email}>"
