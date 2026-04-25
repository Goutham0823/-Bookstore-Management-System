from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from .permissions import IsAdmin, IsCustomer, IsOrderOwnerOrAdmin


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderListCreateView(APIView):
    """
    GET  /api/orders/ — List all orders (Admin only, paginated)
    POST /api/orders/ — Place a new order (Customer only)
    """
    pagination_class = OrderPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsCustomer()]

    @extend_schema(
        tags=['Orders'],
        summary='List all orders — Admin only',
        description='Returns a paginated list of every order in the system. Requires ADMIN role.',
        parameters=[OpenApiParameter('page', int, description='Page number')],
        responses={
            200: OrderSerializer(many=True),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Admin access required'),
        },
    )
    def get(self, request):
        orders = Order.objects.select_related('user').prefetch_related('items__book').all()
        paginator = OrderPagination()
        page = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=['Orders'],
        summary='Place a new order — Customer only',
        description='Creates a new order, decrements book stock, and calculates total. Requires CUSTOMER role.',
        request=OrderCreateSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description='Validation error (insufficient stock, invalid book, etc.)'),
            403: OpenApiResponse(description='Customer access required'),
        },
    )
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Orders'],
    summary='Retrieve a single order',
    description='Returns order details. Accessible by the order owner or any admin.',
    responses={
        200: OrderSerializer,
        403: OpenApiResponse(description='Not authorized to view this order'),
        404: OpenApiResponse(description='Order not found'),
    },
)
class OrderDetailView(generics.RetrieveAPIView):
    """GET /api/orders/{id}/ — Order owner or Admin."""
    queryset = Order.objects.select_related('user').prefetch_related('items__book').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrAdmin]


@extend_schema(
    tags=['Orders'],
    summary='Update order status — Admin only',
    description='Update the order status and/or payment status. Requires ADMIN role.',
    request=OrderStatusUpdateSerializer,
    responses={
        200: OrderSerializer,
        400: OpenApiResponse(description='Invalid status value'),
        403: OpenApiResponse(description='Admin access required'),
        404: OpenApiResponse(description='Order not found'),
    },
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdmin])
def order_status_update(request, pk):
    """PUT /api/orders/{id}/status/ — Admin only: update order/payment status."""
    try:
        order = Order.objects.select_related('user').prefetch_related('items__book').get(pk=pk)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(OrderSerializer(order).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
