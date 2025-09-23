from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from apps.core.models import CompanyProfile
from .models import Role, UserRole
from .managers import UserRoleManager, PermissionChecker
from .decorators import require_permission, require_role, api_permission_required
from .forms import UserRoleAssignmentForm, RoleForm, SuperAdminUserCreationForm, UserEditForm, BulkUserCreationForm

User = get_user_model()


@login_required
@require_role('company_admin')
def role_management(request):
    """Main role management dashboard"""
    # Use company from middleware if available, otherwise fallback to user's company profile
    company = getattr(request, 'user_company', None)
    if not company:
        company = request.user.company_profile
    user_roles = UserRole.objects.filter(company=company, is_active=True).select_related('user', 'role')
    
    # Pagination
    paginator = Paginator(user_roles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_users': user_roles.count(),
        'available_roles': Role.objects.filter(is_active=True),
    }
    
    return render(request, 'rbac/role_management.html', context)


@login_required
@require_role('company_admin')
def assign_role(request):
    """Assign role to a user"""
    # Use company from middleware if available, otherwise fallback to user's company profile
    company = getattr(request, 'user_company', None)
    if not company:
        company = request.user.company_profile
    
    if request.method == 'POST':
        form = UserRoleAssignmentForm(request.POST, company=company)
        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']
            expires_at = form.cleaned_data.get('expires_at')
            
            try:
                user_role, created = UserRoleManager.assign_role(
                    user=user,
                    company=company,
                    role_type=role.role_type,
                    assigned_by=request.user,
                    expires_at=expires_at
                )
                
                if created:
                    messages.success(request, f'Successfully assigned {role.name} role to {user.get_full_name()}.')
                else:
                    messages.warning(request, f'{user.get_full_name()} already has the {role.name} role.')
                
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'Role assigned successfully',
                        'user_role_id': user_role.id
                    })
                
                return redirect('rbac:role_management')
            
            except Exception as e:
                messages.error(request, f'Error assigning role: {str(e)}')
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)
    else:
        form = UserRoleAssignmentForm(company=company)
    
    context = {
        'form': form,
        'company': company,
    }
    
    return render(request, 'rbac/assign_role.html', context)


@login_required
@require_role('company_admin')
def revoke_role(request, user_role_id):
    """Revoke a role from a user"""
    # Use company from middleware if available, otherwise fallback to user's company profile
    company = getattr(request, 'user_company', None)
    if not company:
        company = request.user.company_profile
    user_role = get_object_or_404(UserRole, id=user_role_id, company=company)
    
    if request.method == 'POST':
        user_role.is_active = False
        user_role.save()
        
        messages.success(request, f'Successfully revoked {user_role.role.name} role from {user_role.user.get_full_name()}.')
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Role revoked successfully'
            })
        
        return redirect('rbac:role_management')
    
    context = {
        'user_role': user_role,
    }
    
    return render(request, 'rbac/revoke_role.html', context)


@login_required
@require_permission('rbac.view_role')
def role_list(request):
    """List all available roles"""
    roles = Role.objects.filter(is_active=True).prefetch_related('permissions')
    
    context = {
        'roles': roles,
    }
    
    return render(request, 'rbac/role_list.html', context)


@login_required
@require_permission('rbac.view_userrole')
def user_role_history(request, user_id):
    """View role history for a specific user"""
    user = get_object_or_404(User, id=user_id)
    user_roles = UserRole.objects.filter(user=user).select_related('company', 'role', 'assigned_by').order_by('-assigned_at')
    
    context = {
        'user': user,
        'user_roles': user_roles,
    }
    
    return render(request, 'rbac/user_role_history.html', context)


@login_required
def my_permissions(request):
    """View current user's permissions"""
    # Use company from middleware if available, otherwise fallback to user's company profile
    company = getattr(request, 'user_company', None)
    if not company and hasattr(request.user, 'company_profile'):
        company = request.user.company_profile
    user_roles = UserRoleManager.get_user_roles(request.user, company)
    permissions = PermissionChecker.get_user_permissions(request.user, company)
    
    context = {
        'user_roles': user_roles,
        'permissions': permissions,
        'company': company,
    }
    
    return render(request, 'rbac/my_permissions.html', context)


# API Views
@api_permission_required('rbac.view_userrole')
def api_user_roles(request):
    """API endpoint to get user roles"""
    # Use company from middleware if available, otherwise fallback to user's company profile
    company = getattr(request, 'user_company', None)
    if not company:
        company = request.user.company_profile
    user_roles = UserRole.objects.filter(company=company, is_active=True).select_related('user', 'role')
    
    data = []
    for user_role in user_roles:
        data.append({
            'id': user_role.id,
            'user': {
                'id': user_role.user.id,
                'name': user_role.user.get_full_name(),
                'email': user_role.user.email,
            },
            'role': {
                'id': user_role.role.id,
                'name': user_role.role.name,
                'type': user_role.role.role_type,
            },
            'assigned_at': user_role.assigned_at.isoformat(),
            'expires_at': user_role.expires_at.isoformat() if user_role.expires_at else None,
            'is_expired': user_role.is_expired(),
        })
    
    return JsonResponse({'data': data})


@api_permission_required('rbac.add_userrole')
@require_http_methods(["POST"])
def api_assign_role(request):
    """API endpoint to assign role"""
    # Use company from middleware if available, otherwise fallback to user's company profile
    company = getattr(request, 'user_company', None)
    if not company:
        company = request.user.company_profile
    
    try:
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        expires_at = request.POST.get('expires_at')
        
        if not user_id or not role_id:
            return JsonResponse({'error': 'User ID and Role ID are required'}, status=400)
        
        user = User.objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
        
        user_role, created = UserRoleManager.assign_role(
            user=user,
            company=company,
            role_type=role.role_type,
            assigned_by=request.user,
            expires_at=expires_at if expires_at else None
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Role assigned successfully',
            'user_role_id': user_role.id,
            'created': created
        })
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_permission_required('rbac.delete_userrole')
@require_http_methods(["POST"])
def api_revoke_role(request, user_role_id):
    """API endpoint to revoke role"""
    try:
        # Use company from middleware if available, otherwise fallback to user's company profile
        company = getattr(request, 'user_company', None)
        if not company:
            company = request.user.company_profile
        user_role = UserRole.objects.get(
            id=user_role_id,
            company=company
        )
        
        user_role.is_active = False
        user_role.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Role revoked successfully'
        })
    
    except UserRole.DoesNotExist:
        return JsonResponse({'error': 'User role not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_permission_required('rbac.view_role')
def api_roles(request):
    """API endpoint to get available roles"""
    roles = Role.objects.filter(is_active=True)
    
    data = []
    for role in roles:
        data.append({
            'id': role.id,
            'name': role.name,
            'type': role.role_type,
            'description': role.description,
            'permissions_count': role.permissions.count(),
        })
    
    return JsonResponse({'data': data})


@login_required
def search_users(request):
    """Search users for role assignment"""
    query = request.GET.get('q', '')
    # Use company from middleware if available, otherwise fallback to user's company profile
    company = getattr(request, 'user_company', None)
    if not company:
        company = request.user.company_profile
    
    if query:
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(
            user_roles__company=company,
            user_roles__is_active=True
        )[:10]
    else:
        users = User.objects.none()
    
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
        })
    
    return JsonResponse({'data': data})


# Super Admin User Management Views
@login_required
@require_role('super_admin')
def super_admin_user_management(request):
    """Super admin user management dashboard"""
    users = User.objects.all().select_related().prefetch_related('user_roles__role', 'user_roles__company').order_by('-date_joined', 'id')
    
    # Pagination
    paginator = Paginator(users, 10)  # Changed to 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_users': users.count(),
        'companies': CompanyProfile.objects.all(),
        'roles': Role.objects.filter(is_active=True),
    }
    
    return render(request, 'rbac/super_admin_user_management.html', context)


@login_required
@require_role('super_admin')
def create_user(request):
    """Create new user with role assignment"""
    if request.method == 'POST':
        form = SuperAdminUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Create the user
                user = form.save()
                
                # Assign role to the user
                company = form.cleaned_data['company']
                role = form.cleaned_data['role']
                expires_at = form.cleaned_data.get('expires_at')
                
                user_role, created = UserRoleManager.assign_role(
                    user=user,
                    company=company,
                    role_type=role.role_type,
                    assigned_by=request.user,
                    expires_at=expires_at
                )
                
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'User {user.get_full_name()} created successfully with {role.name} role',
                        'user_id': user.id,
                        'user_role_id': user_role.id
                    })
                
                messages.success(request, f'User {user.get_full_name()} created successfully with {role.name} role.')
                return redirect('rbac:super_admin_user_management')
            
            except Exception as e:
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)
                messages.error(request, f'Error creating user: {str(e)}')
    else:
        form = SuperAdminUserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'rbac/create_user.html', context)


@login_required
@require_role('super_admin')
def edit_user(request, user_id):
    """Edit existing user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'User {user.get_full_name()} updated successfully'
                    })
                
                messages.success(request, f'User {user.get_full_name()} updated successfully.')
                return redirect('rbac:super_admin_user_management')
            
            except Exception as e:
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)
                messages.error(request, f'Error updating user: {str(e)}')
    else:
        form = UserEditForm(instance=user)
    
    # Get user's current roles
    user_roles = UserRole.objects.filter(user=user, is_active=True).select_related('role', 'company')
    
    context = {
        'form': form,
        'user': user,
        'user_roles': user_roles,
    }
    
    return render(request, 'rbac/edit_user.html', context)


@login_required
@require_role('super_admin')
def bulk_create_users(request):
    """Bulk create users from CSV data"""
    if request.method == 'POST':
        form = BulkUserCreationForm(request.POST)
        if form.is_valid():
            try:
                import csv
                from io import StringIO
                
                users_data = form.cleaned_data['users_data']
                company = form.cleaned_data['company']
                default_password = form.cleaned_data['default_password']
                send_welcome_email = form.cleaned_data.get('send_welcome_email', False)
                
                # Parse CSV data
                csv_file = StringIO(users_data)
                reader = csv.DictReader(csv_file)
                
                created_users = []
                errors = []
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                    try:
                        # Create user
                        user = User.objects.create_user(
                            email=row['email'],
                            password=default_password,
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            phone=row.get('phone', ''),
                            is_active=True
                        )
                        
                        # Assign role
                        role_type = row.get('role_type', 'viewer')
                        try:
                            role = Role.objects.get(role_type=role_type)
                            user_role, created = UserRoleManager.assign_role(
                                user=user,
                                company=company,
                                role_type=role_type,
                                assigned_by=request.user
                            )
                        except Role.DoesNotExist:
                            errors.append(f'Row {row_num}: Role type "{role_type}" not found')
                            user.delete()
                            continue
                        
                        created_users.append(user)
                        
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
                
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully created {len(created_users)} users',
                        'created_count': len(created_users),
                        'errors': errors
                    })
                
                if created_users:
                    messages.success(request, f'Successfully created {len(created_users)} users.')
                if errors:
                    for error in errors:
                        messages.error(request, error)
                
                return redirect('rbac:super_admin_user_management')
            
            except Exception as e:
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)
                messages.error(request, f'Error in bulk creation: {str(e)}')
    else:
        form = BulkUserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'rbac/bulk_create_users.html', context)


# API Views for Super Admin
@api_permission_required('rbac.add_user')
@require_http_methods(["POST"])
def api_create_user(request):
    """API endpoint to create user"""
    try:
        form = SuperAdminUserCreationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Assign role to the user
            company = form.cleaned_data['company']
            role = form.cleaned_data['role']
            expires_at = form.cleaned_data.get('expires_at')
            
            user_role, created = UserRoleManager.assign_role(
                user=user,
                company=company,
                role_type=role.role_type,
                assigned_by=request.user,
                expires_at=expires_at
            )
            
            return JsonResponse({
                'success': True,
                'message': f'User {user.get_full_name()} created successfully',
                'user': {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                },
                'user_role_id': user_role.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@api_permission_required('rbac.change_user')
@require_http_methods(["POST"])
def api_edit_user(request, user_id):
    """API endpoint to edit user"""
    try:
        user = User.objects.get(id=user_id)
        form = UserEditForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            
            return JsonResponse({
                'success': True,
                'message': f'User {user.get_full_name()} updated successfully',
                'user': {
                    'id': user.id,
                    'name': user.get_full_name(),
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@api_permission_required('rbac.view_user')
def api_users_list(request):
    """API endpoint to get users list with pagination"""
    users = User.objects.all().select_related().prefetch_related('user_roles__role', 'user_roles__company').order_by('-date_joined', 'id')
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    data = []
    for index, user in enumerate(page_obj):
        user_roles = []
        for user_role in user.user_roles.filter(is_active=True):
            user_roles.append({
                'id': user_role.id,
                'role_name': user_role.role.name,
                'role_type': user_role.role.role_type,
                'company_name': user_role.company.company_name,
                'assigned_at': user_role.assigned_at.isoformat(),
                'expires_at': user_role.expires_at.isoformat() if user_role.expires_at else None,
            })
        
        data.append({
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'phone': user.phone,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined.isoformat(),
            'user_roles': user_roles,
            'serial_number': page_obj.start_index() + index,
        })
    
    return JsonResponse({
        'data': data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': page_obj.paginator.num_pages,
            'total_count': page_obj.paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
        }
    })


@api_permission_required('rbac.delete_user')
@require_http_methods(["POST"])
def api_delete_user(request, user_id):
    """API endpoint to delete user"""
    try:
        user = User.objects.get(id=user_id)
        user_name = user.get_full_name()
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'User {user_name} deleted successfully'
        })
    
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)