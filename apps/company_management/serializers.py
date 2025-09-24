from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company, CompanyUser, CompanySettings
from apps.rbac.models import Role

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'website',
            'registration_number', 'tax_id', 'industry', 'status',
            'is_active', 'created_at', 'updated_at', 'created_by',
            'created_by_name', 'user_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_user_count(self, obj):
        return obj.company_users.filter(is_active=True).count()


class CompanyUserSerializer(serializers.ModelSerializer):
    """Serializer for CompanyUser model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    class Meta:
        model = CompanyUser
        fields = [
            'id', 'user', 'user_name', 'user_email', 'company', 'company_name',
            'role', 'role_name', 'is_active', 'is_primary', 'assigned_at',
            'expires_at', 'assigned_by', 'assigned_by_name'
        ]
        read_only_fields = ['id', 'assigned_at', 'assigned_by']


class CompanySettingsSerializer(serializers.ModelSerializer):
    """Serializer for CompanySettings model"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = CompanySettings
        fields = [
            'id', 'company', 'company_name', 'default_currency',
            'default_tax_rate', 'business_hours', 'timezone',
            'enable_invoicing', 'enable_inventory', 'enable_accounting',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating companies"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'email', 'phone', 'address', 'website',
            'registration_number', 'tax_id', 'industry', 'status'
        ]
    
    def create(self, validated_data):
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CompanyUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating company user assignments"""
    
    class Meta:
        model = CompanyUser
        fields = ['user', 'company', 'role', 'is_primary', 'expires_at']
    
    def create(self, validated_data):
        # Set the assigned_by field to the current user
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        # Check if user is already assigned to this company
        if CompanyUser.objects.filter(
            user=data['user'],
            company=data['company'],
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "This user is already assigned to this company."
            )
        return data


class CompanyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for company lists"""
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'email', 'phone', 'status', 'is_active',
            'created_at', 'user_count'
        ]
    
    def get_user_count(self, obj):
        return obj.company_users.filter(is_active=True).count()
