import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
)


logger = logging.getLogger(__name__)


class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        try:
            serializer = RegisterSerializer(
                data=request.data
            )

            if not serializer.is_valid():

                return Response(
                    {
                        "status": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Registration failed.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()

            return Response(
                {
                    "status": True,
                    "status_code": status.HTTP_201_CREATED,
                    "message": "User registered successfully.",
                    "data": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception:

            logger.exception(
                "Unexpected error during user registration"
            )

            return Response(
                {
                    "status": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": (
                        "Something went wrong. "
                        "Please try again later."
                    ),
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        try:
            serializer = LoginSerializer(
                data=request.data
            )

            if not serializer.is_valid():

                return Response(
                    {
                        "status": False,
                        "status_code": status.HTTP_401_UNAUTHORIZED,
                        "message": "Login failed.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            data = serializer.validated_data
            user = data["user"]

            return Response(
                {
                    "status": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Login successful.",
                    "data": {
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                        },
                        "tokens": {
                            "access": data["access"],
                            "refresh": data["refresh"],
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception:

            logger.exception(
                "Unexpected error during user login"
            )

            return Response(
                {
                    "status": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": (
                        "Something went wrong. "
                        "Please try again later."
                    ),
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )