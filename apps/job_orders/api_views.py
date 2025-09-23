from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Product, Order
from .views import get_user_currency_symbol

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    API endpoint to get dashboard statistics for real-time updates
    """
    try:
        # Product Statistics
        product_count = Product.objects.count()
        
        # Order Statistics
        order_count = Order.objects.count()
        
        # User Statistics
        customer_count = User.objects.filter(is_active=True).count()
        
        # Pending Orders Statistics
        pending_count = Product.objects.filter(approval_status='pending').count()
        
        # Currency symbol
        currency_symbol = get_user_currency_symbol(request.user)
        
        return Response({
            'success': True,
            'data': {
                'product_count': product_count,
                'order_count': order_count,
                'customer_count': customer_count,
                'pending_count': pending_count,
                'currency_symbol': currency_symbol,
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
