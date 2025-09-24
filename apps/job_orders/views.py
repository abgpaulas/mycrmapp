from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models.functions import TruncSecond
from zoneinfo import ZoneInfo
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from .models import Product, Order, Leave, ProductStatusHistory, Customer, Store, StoreInventory, StockMovement, Waybill, Receipt, Invoice
from .forms import ProductForm, OrderForm, LeaveForm, CustomerForm, StoreForm, StoreInventoryForm, StockMovementForm, WaybillForm, ReceiptForm, InvoiceForm, ProductStatusHistoryForm
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg, Min, Max
from reportlab.platypus import Image, Spacer
import os
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import send_mail
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.core.cache import cache
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models.functions import TruncDate
import logging

logger = logging.getLogger(__name__)
wat_timezone = ZoneInfo("Africa/Lagos")

def is_staff_member(user):
    return user.is_staff or user.groups.filter(name='Staff').exists()

def get_user_currency_symbol(user):
    """Get currency symbol from user's company profile"""
    try:
        if user and hasattr(user, 'company_profile'):
            return user.company_profile.currency_symbol
    except:
        pass
    return '₦'  # Default fallback

@login_required(login_url='auth:login')
def index(request):
    # Product Statistics
    product = Product.objects.all()
    product_count = product.count()
    
    # Order Statistics
    order = Order.objects.all()
    order_count = order.count()
    
    # User Statistics
    customer = User.objects.filter(is_active=True)
    customer_count = customer.count()
    
    # Role-based statistics
    if request.user.is_superuser or request.user.groups.filter(name='Leave Manager').exists():
        pending_leaves = Leave.objects.filter(status='pending').order_by('-created_at')
        pending_leaves_count = pending_leaves.count()
        staff_count = Leave.objects.all().count()
    else:
        pending_leaves = Leave.objects.filter(employee=request.user, status='pending').order_by('-created_at')
        pending_leaves_count = pending_leaves.count()
        staff_count = Leave.objects.filter(employee=request.user).count()

    context = {
        'product': product,
        'product_count': product_count,
        'order_count': order_count,
        'customer_count': customer_count,
        'staff_count': staff_count,
        'pending_leaves': pending_leaves[:5],
        'pending_leaves_count': pending_leaves_count,
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required(login_url='auth:login')
@permission_required('job_orders.can_view_all_jobs', raise_exception=True)
def products(request):
    # Initialize form with user
    form = ProductForm(user=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.calculate_total()
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
                
            product.save()
            messages.success(request, f'Job Order {product.job_order} has been added and is pending approval')
            return redirect('job_orders:products')

    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    filter_status = request.GET.get('status', '')
    
    # Base queryset
    products = Product.objects.annotate(
        local_date_created=TruncSecond('date_created', tzinfo=wat_timezone)
    ).order_by('-local_date_created')
    
    # Apply filters if present
    if search_query:
        products = products.filter(
            Q(job_order__icontains=search_query) |
            Q(organization_name__icontains=search_query) |
            Q(job_title__icontains=search_query)
        )
    
    if filter_status:
        products = products.filter(approval_status=filter_status)
    
    # Pagination - Show 5 products per page
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate pending count
    pending_count = products.filter(approval_status='pending').count()
    
    context = {
        'products': page_obj,
        'form': form,
        'customer_count': User.objects.filter(is_active=True).count(),
        'product_count': products.count(),
        'order_count': Order.objects.count(),
        'pending_count': pending_count,
        'currency_symbol': get_user_currency_symbol(request.user),
    }
    
    return render(request, 'job_orders/products.html', context)

@login_required(login_url='auth:login')
@permission_required('job_orders.can_approve_jobs', raise_exception=True)
def approve_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get('action')
    
    if action in ['approved', 'pending', 'rejected']:
        product.approval_status = action
        product.approved_by = request.user
        product.save()
        
        # Log the status change
        ProductStatusHistory.objects.create(
            product=product,
            status=action,
            updated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Product status updated to {action}'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid action specified'
    })

@login_required
@permission_required('job_orders.can_view_all_jobs', raise_exception=True)
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    if request.method == 'POST':
        form = ProductForm(
            data=request.POST,
            files=request.FILES,
            instance=product,
            user=request.user
        )
        if form.is_valid():
            product = form.save(commit=False)
            product.updated_by = request.user
            product.calculate_total()
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('job_orders:product_detail', pk=pk)
    else:
        form = ProductForm(instance=product, user=request.user)
    
    context = {
        'product': product,
        'form': form,
        'currency_symbol': get_user_currency_symbol(request.user),
    }
    return render(request, 'job_orders/product_detail.html', context)

@login_required
@permission_required('job_orders.can_view_all_jobs', raise_exception=True)
def product_edit(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    if request.method == 'POST':
        form = ProductForm(
            data=request.POST,
            files=request.FILES,
            instance=product,
            user=request.user
        )
        if form.is_valid():
            product = form.save(commit=False)
            product.updated_by = request.user
            product.calculate_total()
            product.save()
            
            # Handle Ajax requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Product updated successfully!',
                    'product_data': {
                        'id': product.id,
                        'job_order': product.job_order,
                        'organization_name': product.organization_name,
                        'address': product.address,
                        'contact_number': product.contact_number,
                        'print_product': product.print_product,
                        'colors': product.colors,
                        'treatment': product.treatment,
                        'cutting_length': product.cutting_length,
                        'flap': product.flap,
                        'printing': product.printing,
                        'size': product.size,
                        'micron': product.micron,
                        'job_title': product.job_title,
                        'order_info': product.order_info,
                        'quantity': product.quantity,
                        'price': str(product.price) if product.price else '',
                        'order_quantity': product.order_quantity,
                        'total': str(product.total) if product.total else '',
                        'estimated_delivery_date': product.estimated_delivery_date.strftime('%Y-%m-%d') if product.estimated_delivery_date else '',
                        'actual_delivery_date': product.actual_delivery_date.strftime('%Y-%m-%d') if product.actual_delivery_date else '',
                        'approval_status': product.approval_status,
                        'approval_status_display': product.get_approval_status_display(),
                        'approved_by': product.approved_by.email if product.approved_by else '',
                        'created_by': product.created_by.email if product.created_by else '',
                        'formatted_price': product.formatted_price(),
                        'formatted_total': product.formatted_total(),
                        'updated_by': product.updated_by.email if product.updated_by else '',
                        'updated_at': product.production_status_date.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                })
            
            messages.success(request, 'Product updated successfully!')
            return redirect('job_orders:product_detail', pk=pk)
        else:
            # Handle Ajax validation errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': form.errors
                })
    else:
        form = ProductForm(instance=product, user=request.user)
    
    context = {
        'product': product,
        'form': form,
        'currency_symbol': get_user_currency_symbol(request.user),
    }
    return render(request, 'job_orders/product_edit.html', context)

@login_required
@permission_required('job_orders.can_view_all_jobs', raise_exception=True)
def product_delete(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('job_orders:products')
    
    context = {
        'product': product,
        'currency_symbol': get_user_currency_symbol(request.user),
    }
    return render(request, 'job_orders/product_delete.html', context)

@login_required
def product_view(request, job_id):
    try:
        product = Product.objects.get(job_order=job_id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found!')
        return redirect('job_orders:products')
    
    # Get status history for this product
    status_history = ProductStatusHistory.objects.filter(product=product, is_active=True).order_by('-created_at')
    
    context = {
        'product': product,
        'status_history': status_history,
        'currency_symbol': get_user_currency_symbol(request.user),
    }
    return render(request, 'job_orders/product_view.html', context)

@login_required
@permission_required('job_orders.can_export_products', raise_exception=True)
def export_products_pdf(request):
    products = Product.objects.all().order_by('-date_created')
    
    # Calculate statistics
    pending_count = products.filter(approval_status='pending').count()
    approved_count = products.filter(approval_status='approved').count()
    rejected_count = products.filter(approval_status='rejected').count()
    total_value = sum(product.total or 0 for product in products)
    
    # Debug: Log product count
    logger.info(f"Exporting {products.count()} products to PDF")
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="products_report.pdf"'
    
    template = get_template('job_orders/products_pdf.html')
    html = template.render({
        'products': products,
        'currency_symbol': get_user_currency_symbol(request.user),
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_value': total_value,
    })
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        logger.error(f"PDF generation error: {pisa_status.err}")
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
@permission_required('job_orders.can_export_products', raise_exception=True)
def export_single_product_pdf(request, job_id):
    try:
        product = Product.objects.get(job_order=job_id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found!')
        return redirect('job_orders:products')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="product_{job_id}.pdf"'
    
    template = get_template('job_orders/product_pdf.html')
    html = template.render({
        'product': product,
        'currency_symbol': get_user_currency_symbol(request.user),
    })
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
@permission_required('job_orders.can_export_products', raise_exception=True)
def export_product_view_pdf(request, job_id):
    try:
        product = Product.objects.get(job_order=job_id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found!')
        return redirect('job_orders:products')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="product_view_{job_id}.pdf"'
    
    template = get_template('job_orders/product_view_pdf.html')
    html = template.render({
        'product': product,
        'currency_symbol': get_user_currency_symbol(request.user),
    })
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
@permission_required('job_orders.can_manage_production', raise_exception=True)
def update_production_status(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_status = request.POST.get('new_status')
        priority = request.POST.get('priority', 1)  # Default to normal priority
        
        try:
            product = Product.objects.get(id=product_id)
            ProductStatusHistory.objects.create(
                product=product,
                status=new_status,
                priority=int(priority),
                updated_by=request.user
            )
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid priority value'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@permission_required('job_orders.can_manage_production', raise_exception=True)
def delete_status_history(request, history_id):
    try:
        history = ProductStatusHistory.objects.get(id=history_id)
        # Check if user is super admin or the one who created the status
        if request.user.is_superuser or history.updated_by == request.user:
            history.delete()
            return JsonResponse({'success': True, 'message': 'Status update deleted successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'You do not have permission to delete this status update'})
    except ProductStatusHistory.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Status update not found'})

@login_required
@permission_required('job_orders.can_manage_production', raise_exception=True)
def edit_status_history(request, history_id):
    if request.method == 'POST':
        try:
            history = ProductStatusHistory.objects.get(id=history_id)
            # Check if user is super admin or the one who created the status
            if request.user.is_superuser or history.updated_by == request.user:
                new_status = request.POST.get('new_status')
                new_priority = request.POST.get('priority', history.priority)
                
                # Update the status history
                history.status = new_status
                history.priority = int(new_priority)
                history.save()
                
                # If this is the most recent status update, also update the product's production_status
                latest_history = ProductStatusHistory.objects.filter(
                    product=history.product, 
                    is_active=True
                ).order_by('-created_at').first()
                
                if latest_history and latest_history.id == history.id:
                    # This is the most recent status, update the product
                    history.product.production_status = new_status
                    history.product.production_status_date = history.created_at
                    history.product.updated_by = request.user
                    history.product.save()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Status update edited successfully',
                    'new_status': new_status,
                    'new_priority': int(new_priority),
                    'new_priority_display': history.get_priority_display()
                })
            else:
                return JsonResponse({'success': False, 'message': 'You do not have permission to edit this status update'})
        except ProductStatusHistory.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Status update not found'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid priority value'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# Customer views
@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    context = {'customers': customers}
    return render(request, 'job_orders/customer_list.html', context)

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('job_orders:customer_list')
    else:
        form = CustomerForm()
    
    context = {'form': form}
    return render(request, 'job_orders/customer_form.html', context)

# Store views
@login_required
def store_list(request):
    stores = Store.objects.all().order_by('-created_at')
    context = {'stores': stores}
    return render(request, 'job_orders/store_list.html', context)

@login_required
def store_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save()
            messages.success(request, 'Store created successfully!')
            return redirect('job_orders:store_list')
    else:
        form = StoreForm()
    
    context = {'form': form}
    return render(request, 'job_orders/store_form.html', context)

# Order views
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-date_created')
    context = {
        'orders': orders,
        'currency_symbol': get_user_currency_symbol(request.user),
    }
    return render(request, 'job_orders/order_list.html', context)

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.save()
            messages.success(request, 'Order created successfully!')
            return redirect('job_orders:order_list')
    else:
        form = OrderForm()
    
    context = {'form': form}
    return render(request, 'job_orders/order_form.html', context)

# Leave views
@login_required
def leave_list(request):
    if request.user.is_superuser:
        leaves = Leave.objects.all().order_by('-created_at')
    else:
        leaves = Leave.objects.filter(employee=request.user).order_by('-created_at')
    
    context = {'leaves': leaves}
    return render(request, 'job_orders/leave_list.html', context)

@login_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('job_orders:leave_list')
    else:
        form = LeaveForm()
    
    context = {'form': form}
    return render(request, 'job_orders/leave_form.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_job_order_currency(request):
    """Update currency across all job order features"""
    try:
        import json
        data = json.loads(request.body)
        currency_code = data.get('currency_code')
        currency_symbol = data.get('currency_symbol')
        
        if not currency_code or not currency_symbol:
            return JsonResponse({'success': False, 'error': 'Currency code and symbol are required'})
        
        # Update company profile currency
        company_profile = request.user.company_profile
        company_profile.currency_code = currency_code
        company_profile.currency_symbol = currency_symbol
        company_profile.save()
        
        # Update all job order products to trigger recalculation
        products = Product.objects.filter(created_by=request.user)
        updated_products = 0
        
        for product in products:
            # Trigger save to update currency displays
            product.save()
            updated_products += 1
        
        # Update all orders
        orders = Order.objects.filter(customer=request.user)
        updated_orders = 0
        
        for order in orders:
            # Trigger save to update currency displays
            order.save()
            updated_orders += 1
        
        # Update accounting transactions if they exist
        transactions_updated = 0
        try:
            from apps.accounting.models import Transaction
            transactions_updated = Transaction.objects.filter(
                company=company_profile,
                source_app='job_order'
            ).update(currency=currency_symbol)
        except ImportError:
            # Accounting app might not be installed
            pass
        except Exception as e:
            print(f"Warning: Failed to update job order transactions: {e}")
        
        return JsonResponse({
            'success': True,
            'currency_code': currency_code,
            'currency_symbol': currency_symbol,
            'products_updated': updated_products,
            'orders_updated': updated_orders,
            'transactions_updated': transactions_updated,
            'message': f'Successfully updated job order currency to {currency_code} ({currency_symbol}). {updated_products} products, {updated_orders} orders, and {transactions_updated} transactions updated.'
        })
        
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data provided'})
    except Exception as e:
        import traceback
        print(f"Job order currency update error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': f'Failed to update job order currency: {str(e)}'})