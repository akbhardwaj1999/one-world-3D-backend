from rest_framework import serializers
from .models import (
    Story, ArtControlSettings, Chat,
    Talent, CharacterTalentAssignment,
    AssetTalentAssignment, ShotTalentAssignment
)


class ArtControlSettingsSerializer(serializers.ModelSerializer):
    """Serializer for Art Control Settings"""
    story_id = serializers.IntegerField(source='story.id', read_only=True, allow_null=True)
    story_title = serializers.CharField(source='story.title', read_only=True, allow_null=True)
    sequence_id = serializers.IntegerField(source='sequence.id', read_only=True, allow_null=True)
    shot_id = serializers.IntegerField(source='shot.id', read_only=True, allow_null=True)
    
    class Meta:
        model = ArtControlSettings
        fields = [
            'id',
            'story_id',
            'story_title',
            'sequence_id',
            'shot_id',
            # Color Palette
            'primary_colors',
            'color_mood',
            'color_saturation',
            'color_contrast',
            'forbidden_colors',
            # Composition
            'composition_style',
            'preferred_shot_types',
            # Camera Guidelines
            'handheld_allowed',
            'stable_camera_allowed',
            'gimbal_allowed',
            'drone_allowed',
            'static_camera_allowed',
            # Lens Guidelines
            'wide_angle_allowed',
            'standard_lens_preferred',
            'telephoto_allowed',
            'macro_allowed',
            'fisheye_allowed',
            # Camera Movement
            'static_shots_only',
            'panning_allowed',
            'tracking_allowed',
            'zoom_allowed',
            'dolly_shots_allowed',
            # Visual Style
            'art_style',
            'detail_level',
            'lighting_style',
            # Animation Style
            'animation_type',
            'motion_preference',
            # Reference Images
            'style_reference_images',
            'mood_board_images',
            # Story Level - Technical Specifications
            'frame_rate',
            'resolution',
            # Aspect Ratio
            'aspect_ratio',
            'custom_aspect_ratio',
            # Sequence/Shot Level - Environment & Timing
            'atmosphere',
            'time_of_day',
            'shot_duration',
            # Metadata
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatSerializer(serializers.ModelSerializer):
    """Serializer for Chat"""
    
    class Meta:
        model = Chat
        fields = ['id', 'title', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_messages(self, value):
        """Validate messages is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Messages must be a list")
        return value


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
