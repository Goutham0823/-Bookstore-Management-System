from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer


@extend_schema(
    tags=['Authentication'],
    summary='Register a new user',
    description='Creates a new CUSTOMER or ADMIN account. Password must be at least 8 characters.',
    request=RegisterSerializer,
    responses={
        201: RegisterSerializer,
        400: OpenApiResponse(description='Validation errors (duplicate email, password mismatch, etc.)'),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new CUSTOMER or ADMIN user."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {'message': 'User registered successfully.', 'user': RegisterSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Login and obtain JWT tokens',
    description='Authenticates a user and returns access + refresh JWT tokens.',
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description='Returns access and refresh JWT tokens'),
        400: OpenApiResponse(description='Invalid credentials'),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Authenticate user and return JWT access + refresh tokens."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = serializer.get_tokens(user)
        return Response(
            {'message': 'Login successful.', 'user': UserProfileSerializer(user).data, 'tokens': tokens},
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Get current user profile',
    responses={200: UserProfileSerializer, 401: OpenApiResponse(description='Authentication required')},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Return the authenticated user's own profile."""
    return Response(UserProfileSerializer(request.user).data)
