from django.contrib import admin
from .models import Talent, CharacterTalentAssignment, AssetTalentAssignment, ShotTalentAssignment


@admin.register(Talent)
class TalentAdmin(admin.ModelAdmin):
    list_display = ['name', 'talent_type', 'email', 'availability_status', 'hourly_rate', 'daily_rate', 'created_at']
    list_filter = ['talent_type', 'availability_status', 'created_at']
    search_fields = ['name', 'email', 'notes']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CharacterTalentAssignment)
class CharacterTalentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['talent', 'character', 'role_type', 'status', 'rate_agreed', 'assigned_at']
    list_filter = ['role_type', 'status', 'assigned_at']
    search_fields = ['talent__name', 'character__name']
    readonly_fields = ['assigned_at', 'updated_at']


@admin.register(AssetTalentAssignment)
class AssetTalentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['talent', 'asset', 'role_type', 'status', 'rate_agreed', 'estimated_hours', 'assigned_at']
    list_filter = ['role_type', 'status', 'assigned_at']
    search_fields = ['talent__name', 'asset__name']
    readonly_fields = ['assigned_at', 'updated_at']


@admin.register(ShotTalentAssignment)
class ShotTalentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['talent', 'shot', 'role_type', 'status', 'rate_agreed', 'estimated_hours', 'assigned_at']
    list_filter = ['role_type', 'status', 'assigned_at']
    search_fields = ['talent__name', 'shot__shot_number']
    readonly_fields = ['assigned_at', 'updated_at']
