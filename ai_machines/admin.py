from django.contrib import admin
from .models import Story, Character, Location, StoryAsset, Shot


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


@admin.register(Shot)
class ShotAdmin(admin.ModelAdmin):
    list_display = ['shot_number', 'story', 'complexity', 'estimated_time']
    list_filter = ['complexity']
    search_fields = ['description']
