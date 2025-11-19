from rest_framework import serializers
from .models import Story, ArtControlSettings, Chat


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
