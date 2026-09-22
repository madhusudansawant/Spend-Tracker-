from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model, password_validation

from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    password2 = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
        ]

    def validate_email(self, value):

        value = value.strip().lower()

        if User.objects.filter(
            email__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate(self, attrs):

        password = attrs["password"]
        password2 = attrs["password2"]

        if password != password2:

            raise serializers.ValidationError({
                "password2": "Passwords do not match."
            })

        password_validation.validate_password(
            password,
            user=None
        )

        return attrs

    def create(self, validated_data):

        validated_data.pop("password2")

        return User.objects.create_user(
            **validated_data
        )


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        email = attrs["email"].strip().lower()
        password = attrs["password"]

        user = authenticate(
            username=email,
            password=password
        )

        if user is None:

            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:

            raise serializers.ValidationError(
                "This account is inactive."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access": str(
                refresh.access_token
            ),
            "refresh": str(refresh),
        }