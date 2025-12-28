from rest_framework import serializers
from .models import (
    Talent, CharacterTalentAssignment,
    AssetTalentAssignment, ShotTalentAssignment
)


class TalentSerializer(serializers.ModelSerializer):
    """Serializer for Talent"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    talent_type_display = serializers.CharField(source='get_talent_type_display', read_only=True)
    availability_status_display = serializers.CharField(source='get_availability_status_display', read_only=True)
    
    class Meta:
        model = Talent
        fields = [
            'id',
            'name',
            'talent_type',
            'talent_type_display',
            'email',
            'phone',
            'portfolio_url',
            'notes',
            'hourly_rate',
            'daily_rate',
            'availability_status',
            'availability_status_display',
            'specializations',
            'languages',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_username',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CharacterTalentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Character Talent Assignment"""
    talent_name = serializers.CharField(source='talent.name', read_only=True)
    talent_type = serializers.CharField(source='talent.talent_type', read_only=True)
    character_name = serializers.CharField(source='character.name', read_only=True)
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CharacterTalentAssignment
        fields = [
            'id',
            'character',
            'character_name',
            'talent',
            'talent_name',
            'talent_type',
            'role_type',
            'role_type_display',
            'status',
            'status_display',
            'rate_agreed',
            'notes',
            'assigned_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'assigned_at', 'updated_at']


class AssetTalentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Asset Talent Assignment"""
    talent_name = serializers.CharField(source='talent.name', read_only=True)
    talent_type = serializers.CharField(source='talent.talent_type', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AssetTalentAssignment
        fields = [
            'id',
            'asset',
            'asset_name',
            'talent',
            'talent_name',
            'talent_type',
            'role_type',
            'role_type_display',
            'status',
            'status_display',
            'rate_agreed',
            'estimated_hours',
            'actual_hours',
            'notes',
            'assigned_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'assigned_at', 'updated_at']


class ShotTalentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Shot Talent Assignment"""
    talent_name = serializers.CharField(source='talent.name', read_only=True)
    talent_type = serializers.CharField(source='talent.talent_type', read_only=True)
    shot_number = serializers.IntegerField(source='shot.shot_number', read_only=True)
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ShotTalentAssignment
        fields = [
            'id',
            'shot',
            'shot_number',
            'talent',
            'talent_name',
            'talent_type',
            'role_type',
            'role_type_display',
            'status',
            'status_display',
            'rate_agreed',
            'estimated_hours',
            'actual_hours',
            'notes',
            'assigned_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'assigned_at', 'updated_at']

