from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.models import CompanyProfile
from .models import Product, Order


@receiver(post_save, sender=CompanyProfile)
def update_job_order_currency_on_company_change(sender, instance, **kwargs):
    """Update job order currency when company profile currency changes"""
    try:
        # Update all products created by users of this company
        products = Product.objects.filter(created_by__company_profile=instance)
        for product in products:
            # Trigger save to update currency displays
            product.save()
        
        # Update all orders for users of this company
        orders = Order.objects.filter(customer__company_profile=instance)
        for order in orders:
            # Trigger save to update currency displays
            order.save()
            
    except Exception as e:
        # Log error but don't fail the company profile save
        print(f"Warning: Failed to update job order currency on company change: {e}")
        pass
