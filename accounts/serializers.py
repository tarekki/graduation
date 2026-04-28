from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from lookups.models import Role
from lookups.serializers import RoleMiniSerializer

User = get_user_model()


def _non_empty_trimmed(value: str | None, field_label: str, max_len: int) -> str:
    text = (value or "").strip()
    if not text:
        raise serializers.ValidationError(f"{field_label} is required.")
    return text[:max_len]


class RegisterSerializer(serializers.Serializer):
    """Accepts registration payload; returns created `User` (handled by view)."""

    first_name = serializers.CharField(max_length=75)
    last_name = serializers.CharField(max_length=75)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.PrimaryKeyRelatedField(
        source="role",
        queryset=Role.objects.all(),
        error_messages={"does_not_exist": "Invalid roleId.", "incorrect_type": "roleId must be an integer."},
    )
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)

    def validate_first_name(self, value):
        return _non_empty_trimmed(value, "First name", 75)

    def validate_last_name(self, value):
        return _non_empty_trimmed(value, "Last name", 75)

    def validate_email(self, value):
        email = (value or "").strip().lower()
        if not email:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.pop("role")
        phone = validated_data.pop("phone_number", None)
        return User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=password,
            role=role,
            phone_number=phone,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class MeSerializer(serializers.ModelSerializer):
    """Profile payload for `/accounts/me/`."""

    role = RoleMiniSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "role", "phone_number")
        read_only_fields = fields
