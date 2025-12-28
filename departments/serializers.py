from rest_framework import serializers
from .models import (
    Department, StoryDepartment,
    AssetDepartmentAssignment, ShotDepartmentAssignment
)


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department"""
    department_type_display = serializers.CharField(source='get_department_type_display', read_only=True)
    assets_count = serializers.SerializerMethodField()
    shots_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'department_type',
            'department_type_display',
            'description',
            'icon',
            'color',
            'is_active',
            'display_order',
            'assets_count',
            'shots_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_assets_count(self, obj):
        """Get count of assets assigned to this department"""
        return obj.asset_assignments.count()
    
    def get_shots_count(self, obj):
        """Get count of shots assigned to this department"""
        return obj.shot_assignments.count()


class StoryDepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Story Department Assignment"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_type = serializers.CharField(source='department.department_type', read_only=True)
    department_icon = serializers.CharField(source='department.icon', read_only=True)
    department_color = serializers.CharField(source='department.color', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = StoryDepartment
        fields = [
            'id',
            'story',
            'department',
            'department_name',
            'department_type',
            'department_icon',
            'department_color',
            'is_active',
            'notes',
            'assigned_at',
            'assigned_by',
            'assigned_by_username',
        ]
        read_only_fields = ['id', 'assigned_at']


class AssetDepartmentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Asset Department Assignment"""
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_type = serializers.CharField(source='asset.asset_type', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_type = serializers.CharField(source='department.department_type', read_only=True)
    department_icon = serializers.CharField(source='department.icon', read_only=True)
    department_color = serializers.CharField(source='department.color', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = AssetDepartmentAssignment
        fields = [
            'id',
            'asset',
            'asset_name',
            'asset_type',
            'department',
            'department_name',
            'department_type',
            'department_icon',
            'department_color',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'due_date',
            'notes',
            'assigned_at',
            'assigned_by',
            'assigned_by_username',
            'updated_at',
        ]
        read_only_fields = ['id', 'assigned_at', 'updated_at']
        extra_kwargs = {
            'asset': {'required': False},
            'department': {'required': False},
        }


class ShotDepartmentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Shot Department Assignment"""
    shot_number = serializers.IntegerField(source='shot.shot_number', read_only=True)
    shot_description = serializers.CharField(source='shot.description', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_type = serializers.CharField(source='department.department_type', read_only=True)
    department_icon = serializers.CharField(source='department.icon', read_only=True)
    department_color = serializers.CharField(source='department.color', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ShotDepartmentAssignment
        fields = [
            'id',
            'shot',
            'shot_number',
            'shot_description',
            'department',
            'department_name',
            'department_type',
            'department_icon',
            'department_color',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'due_date',
            'notes',
            'assigned_at',
            'assigned_by',
            'assigned_by_username',
            'updated_at',
        ]
        read_only_fields = ['id', 'assigned_at', 'updated_at']
        extra_kwargs = {
            'shot': {'required': False},
            'department': {'required': False},
        }

