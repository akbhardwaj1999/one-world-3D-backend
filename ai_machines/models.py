from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Story(models.Model):
    """Story Model - Stores parsed stories"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=255)
    raw_text = models.TextField()
    parsed_data = models.JSONField(default=dict)  # Full parsed JSON
    summary = models.TextField(blank=True)
    total_shots = models.IntegerField(default=0)
    estimated_total_time = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Character(models.Model):
    """Character extracted from story"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    role = models.CharField(max_length=100, blank=True)  # protagonist, antagonist, supporting
    appearances = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'story_characters'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.story.title})"


class Location(models.Model):
    """Location extracted from story"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location_type = models.CharField(max_length=100, blank=True)  # indoor, outdoor, fantasy, etc.
    scenes = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'story_locations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.story.title})"


class StoryAsset(models.Model):
    """Asset extracted from story"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_assets')
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=50)  # model, prop, environment, effect
    description = models.TextField(blank=True)
    complexity = models.CharField(max_length=20, default='medium')  # low, medium, high
    
    class Meta:
        db_table = 'story_assets'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.story.title})"


class Shot(models.Model):
    """Shot extracted from story"""
    COMPLEXITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='shots')
    shot_number = models.IntegerField()
    description = models.TextField()
    characters = models.ManyToManyField(Character, related_name='shots', blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='shots')
    camera_angle = models.CharField(max_length=100, blank=True)
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, default='medium')
    estimated_time = models.CharField(max_length=100, blank=True)
    special_requirements = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'story_shots'
        ordering = ['shot_number']
    
    def __str__(self):
        return f"Shot {self.shot_number} - {self.story.title}"
