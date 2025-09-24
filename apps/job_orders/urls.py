from django.urls import path
from . import views

app_name = 'job_orders'

urlpatterns = [
    # Main products/job orders
    path('', views.products, name='products'),
    path('list/', views.products, name='joborder_list'),  # Alias for products
    path('manufacturing/', views.products, name='manufacturing_joborder_list'),  # Alias for products
    path('layouts/', views.products, name='layout_list'),  # Alias for products
    path('create/', views.products, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('<int:pk>/detail/', views.product_detail, name='manufacturing_joborder_detail'),  # Alias for product_detail
    path('product/<int:product_id>/approve/', views.approve_product, name='approve_product'),
    path('product-view/<str:job_id>/', views.product_view, name='product_view'),
    path('update-production-status/', views.update_production_status, name='update_production_status'),
    path('delete-status-history/<int:history_id>/', views.delete_status_history, name='delete_status_history'),
    path('edit-status-history/<int:history_id>/', views.edit_status_history, name='edit_status_history'),
    
    # Export functions
    path('export-products-pdf/', views.export_products_pdf, name='export_products_pdf'),
    path('export-single-product/<str:job_id>/', views.export_single_product_pdf, name='export_single_product_pdf'),
    path('export-product-view/<str:job_id>/', views.export_product_view_pdf, name='export_product_view_pdf'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    
    # Stores
    path('stores/', views.store_list, name='store_list'),
    path('stores/create/', views.store_create, name='store_create'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    
    # Currency update
    path('update-currency/', views.update_job_order_currency, name='update_job_order_currency'),
    path('orders/create/', views.order_create, name='order_create'),
    
    # Leaves
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/create/', views.leave_create, name='leave_create'),
]
