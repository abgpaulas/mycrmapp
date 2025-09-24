from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
import json

from .models import Company, CompanyUser, CompanySettings
from .forms import CompanyForm, CompanyUserForm, CompanySearchForm
from .serializers import CompanySerializer, CompanyUserSerializer, CompanyListSerializer
from apps.rbac.models import Role

User = get_user_model()


@login_required
def company_list(request):
    """List all companies with search and filter functionality"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:dashboard')
    
    search_form = CompanySearchForm(request.GET)
    companies = Company.objects.all().order_by('-created_at')
    
    # Apply search filters
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        status = search_form.cleaned_data.get('status')
        industry = search_form.cleaned_data.get('industry')
        
        if search:
            companies = companies.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(registration_number__icontains=search)
            )
        
        if status:
            companies = companies.filter(status=status)
        
        if industry:
            companies = companies.filter(industry__icontains=industry)
    
    # Pagination
    paginator = Paginator(companies, 20)
    page_number = request.GET.get('page')
    companies = paginator.get_page(page_number)
    
    context = {
        'companies': companies,
        'search_form': search_form,
        'total_companies': Company.objects.count(),
        'active_companies': Company.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'company_management/company_list.html', context)


@login_required
def company_detail(request, pk):
    """View company details"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:dashboard')
    
    company = get_object_or_404(Company, pk=pk)
    company_users = company.company_users.filter(is_active=True).order_by('-assigned_at')
    
    context = {
        'company': company,
        'company_users': company_users,
    }
    
    return render(request, 'company_management/company_detail.html', context)


@login_required
def company_create(request):
    """Create a new company"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            
            # Create default settings for the company
            CompanySettings.objects.create(company=company)
            
            messages.success(request, f'Company "{company.name}" has been created successfully.')
            return redirect('company_management:company_detail', pk=company.pk)
    else:
        form = CompanyForm()
    
    context = {
        'form': form,
        'title': 'Create New Company',
    }
    
    return render(request, 'company_management/company_form.html', context)


@login_required
def company_edit(request, pk):
    """Edit an existing company"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:dashboard')
    
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f'Company "{company.name}" has been updated successfully.')
            return redirect('company_management:company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'title': f'Edit {company.name}',
    }
    
    return render(request, 'company_management/company_form.html', context)


@login_required
def company_user_assign(request):
    """Assign a user to a company with a role"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = CompanyUserForm(request.POST)
        if form.is_valid():
            company_user = form.save(commit=False)
            company_user.assigned_by = request.user
            company_user.save()
            
            messages.success(
                request,
                f'User "{company_user.user.get_full_name()}" has been assigned to "{company_user.company.name}" as "{company_user.role.name}".'
            )
            return redirect('company_management:company_detail', pk=company_user.company.pk)
    else:
        form = CompanyUserForm()
    
    context = {
        'form': form,
        'title': 'Assign User to Company',
    }
    
    return render(request, 'company_management/company_user_form.html', context)


@login_required
def company_user_remove(request, pk):
    """Remove a user from a company"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:dashboard')
    
    company_user = get_object_or_404(CompanyUser, pk=pk)
    company = company_user.company
    
    if request.method == 'POST':
        company_user.is_active = False
        company_user.save()
        messages.success(
            request,
            f'User "{company_user.user.get_full_name()}" has been removed from "{company.name}".'
        )
        return redirect('company_management:company_detail', pk=company.pk)
    
    context = {
        'company_user': company_user,
        'company': company,
    }
    
    return render(request, 'company_management/company_user_remove.html', context)


# AJAX Views
@login_required
@require_http_methods(["GET"])
def ajax_company_list(request):
    """AJAX endpoint for company list"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    companies = Company.objects.all().order_by('-created_at')
    serializer = CompanyListSerializer(companies, many=True)
    
    return JsonResponse({
        'companies': serializer.data,
        'total': companies.count()
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ajax_company_create(request):
    """AJAX endpoint for creating companies"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        form = CompanyForm(data)
        
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            
            # Create default settings
            CompanySettings.objects.create(company=company)
            
            serializer = CompanySerializer(company)
            return JsonResponse({
                'success': True,
                'message': f'Company "{company.name}" created successfully.',
                'company': serializer.data
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ajax_company_user_assign(request):
    """AJAX endpoint for assigning users to companies"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        form = CompanyUserForm(data)
        
        if form.is_valid():
            company_user = form.save(commit=False)
            company_user.assigned_by = request.user
            company_user.save()
            
            serializer = CompanyUserSerializer(company_user)
            return JsonResponse({
                'success': True,
                'message': f'User assigned successfully.',
                'company_user': serializer.data
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def ajax_get_users(request):
    """AJAX endpoint to get available users for assignment"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    company_id = request.GET.get('company_id')
    if company_id:
        # Get users not already assigned to this company
        users = User.objects.exclude(
            company_users__company_id=company_id,
            company_users__is_active=True
        ).values('id', 'first_name', 'last_name', 'email')
    else:
        users = User.objects.values('id', 'first_name', 'last_name', 'email')
    
    return JsonResponse({'users': list(users)})


@login_required
@require_http_methods(["GET"])
def ajax_get_roles(request):
    """AJAX endpoint to get available roles"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    roles = Role.objects.filter(is_active=True).values('id', 'name', 'role_type')
    return JsonResponse({'roles': list(roles)})