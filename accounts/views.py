from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    Register a new user account and immediately receive JWT tokens.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        summary="Register a new user account",
        description="Creates a new candidate account, hashes the password, and returns JWT tokens.",
        responses={201: RegisterSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            RegisterSerializer(user, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED
        )


class CurrentUserView(generics.RetrieveAPIView):
    """
    Retrieve profile details of the currently authenticated user.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary="Get current user details",
        description="Returns username, email, and joined date for the authenticated user."
    )
    def get_object(self):
        return self.request.user
