from django.contrib import admin
from .models import (
    Story, Character, Location, StoryAsset, Sequence, Shot, ArtControlSettings, Chat,
    Talent, CharacterTalentAssignment, AssetTalentAssignment, ShotTalentAssignment
)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'total_shots', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'summary']


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'story', 'role', 'appearances']
    list_filter = ['role']
    search_fields = ['name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'story', 'location_type', 'scenes']
    list_filter = ['location_type']
    search_fields = ['name']


@admin.register(StoryAsset)
class StoryAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'story', 'asset_type', 'complexity']
    list_filter = ['asset_type', 'complexity']
    search_fields = ['name']


@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    list_display = ['sequence_number', 'title', 'story', 'total_shots', 'estimated_time']
    list_filter = ['story']
    search_fields = ['title', 'description']


@admin.register(Shot)
class ShotAdmin(admin.ModelAdmin):
    list_display = ['shot_number', 'story', 'complexity', 'estimated_time']
    list_filter = ['complexity']
    search_fields = ['description']


@admin.register(ArtControlSettings)
class ArtControlSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_entity_type', 'get_entity_name', 'art_style', 'color_mood', 'updated_at']
    list_filter = ['art_style', 'color_mood', 'created_at']
    search_fields = ['story__title', 'sequence__title', 'shot__description']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_entity_type(self, obj):
        if obj.story:
            return 'Story'
        elif obj.sequence:
            return 'Sequence'
        elif obj.shot:
            return 'Shot'
        return 'Unknown'
    get_entity_type.short_description = 'Type'
    
    def get_entity_name(self, obj):
        if obj.story:
            return obj.story.title
        elif obj.sequence:
            return f"Sequence {obj.sequence.sequence_number}"
        elif obj.shot:
            return f"Shot {obj.shot.shot_number}"
        return 'N/A'
    get_entity_name.short_description = 'Entity'


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Talent)
class TalentAdmin(admin.ModelAdmin):
    list_display = ['name', 'talent_type', 'availability_status', 'hourly_rate', 'daily_rate', 'created_at']
    list_filter = ['talent_type', 'availability_status', 'created_at']
    search_fields = ['name', 'email', 'phone', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'talent_type', 'email', 'phone', 'portfolio_url', 'notes')
        }),
        ('Rates & Availability', {
            'fields': ('hourly_rate', 'daily_rate', 'availability_status')
        }),
        ('Skills & Specializations', {
            'fields': ('specializations', 'languages')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


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
    search_fields = ['talent__name', 'shot__description']
    readonly_fields = ['assigned_at', 'updated_at']
