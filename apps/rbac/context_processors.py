from django.urls import reverse


def rbac_menu_context(request):
    """Context processor to provide role-based menu configuration"""
    if not request.user.is_authenticated:
        return {}
    
    menu_config = [
        {
            'title': 'Dashboard',
            'url': reverse('core:dashboard'),
            'icon': 'dashboard',
            'active_condition': request.resolver_match.view_name == 'core:dashboard',
            'permission': None,  # Everyone can see dashboard
        },
        {
            'title': 'Role Management',
            'url': reverse('rbac:role_management'),
            'icon': 'admin_panel_settings',
            'active_condition': request.resolver_match.app_name == 'rbac',
            'role': 'company_admin',  # Only company admins
        },
        {
            'title': 'Invoices',
            'url': reverse('invoices:list'),
            'icon': 'receipt_long',
            'active_condition': 'invoices' in request.resolver_match.namespace and 'template' not in request.resolver_match.view_name,
            'any_role': ['company_admin', 'manager', 'accountant'],
        },
        {
            'title': 'Invoice Templates',
            'url': reverse('invoices:template_list'),
            'icon': 'palette',
            'active_condition': 'template' in request.resolver_match.view_name,
            'any_role': ['company_admin', 'manager'],
        },
        {
            'title': 'Receipts',
            'url': reverse('receipts:list'),
            'icon': 'receipt',
            'active_condition': request.resolver_match.app_name == 'receipts',
            'any_role': ['company_admin', 'manager', 'accountant'],
        },
        {
            'title': 'Waybills',
            'url': reverse('waybills:list'),
            'icon': 'local_shipping',
            'active_condition': request.resolver_match.app_name == 'waybills',
            'any_role': ['company_admin', 'manager', 'production_manager', 'store_keeper'],
        },
        {
            'title': 'Job Orders',
            'url': reverse('job_orders:products'),
            'icon': 'work',
            'active_condition': request.resolver_match.app_name == 'job_orders',
            'any_role': ['company_admin', 'manager', 'production_manager'],
        },
        {
            'title': 'Job Order Layouts',
            'url': reverse('job_orders:layout_list'),
            'icon': 'table_chart',
            'active_condition': request.resolver_match.app_name == 'job_orders' and request.resolver_match.url_name == 'layout_list',
            'any_role': ['company_admin', 'manager', 'production_manager'],
        },
        {
            'title': 'Quotations',
            'url': reverse('quotations:quotation_list'),
            'icon': 'request_quote',
            'active_condition': request.resolver_match.app_name == 'quotations',
            'any_role': ['company_admin', 'manager', 'marketer'],
        },
        {
            'title': 'Inventory',
            'url': reverse('inventory:dashboard'),
            'icon': 'inventory',
            'active_condition': request.resolver_match.app_name == 'inventory' and 'template' not in request.resolver_match.view_name,
            'any_role': ['company_admin', 'manager', 'production_manager', 'store_keeper'],
        },
        {
            'title': 'Inventory Templates',
            'url': reverse('inventory:template_list'),
            'icon': 'layers',
            'active_condition': 'inventory' in request.resolver_match.app_name and 'template' in request.resolver_match.view_name,
            'any_role': ['company_admin', 'manager', 'store_keeper'],
        },
        {
            'title': 'Clients',
            'url': reverse('clients:client_list'),
            'icon': 'people',
            'active_condition': request.resolver_match.app_name == 'clients',
            'any_role': ['company_admin', 'manager', 'marketer'],
        },
        {
            'title': 'Accounting',
            'url': reverse('accounting:dashboard'),
            'icon': 'bar_chart',
            'active_condition': request.resolver_match.app_name == 'accounting',
            'any_role': ['company_admin', 'manager', 'accountant'],
        },
    ]
    
    return {
        'rbac_menu_config': menu_config,
    }
