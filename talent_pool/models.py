from django.db import models
from django.contrib.auth import get_user_model
from ai_machines.models import Character, StoryAsset, Shot

User = get_user_model()


class Talent(models.Model):
    """Talent pool - External contractors (voice actors, artists, etc.)"""
    TALENT_TYPES = [
        ('voice_actor', 'Voice Actor'),
        ('3d_artist', '3D Artist'),
        ('modeler', '3D Modeler'),
        ('animator', 'Animator'),
        ('rigger', 'Rigger'),
        ('texture_artist', 'Texture Artist'),
        ('lighting_artist', 'Lighting Artist'),
        ('compositor', 'Compositor'),
        ('other', 'Other'),
    ]
    
    AVAILABILITY_STATUS = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('unavailable', 'Unavailable'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=255)
    talent_type = models.CharField(max_length=50, choices=TALENT_TYPES)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    portfolio_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    # Rates & Availability
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default='available'
    )
    
    # Skills & Specializations
    specializations = models.JSONField(default=list, blank=True)  # e.g., ["cartoon", "realistic", "fantasy"]
    languages = models.JSONField(default=list, blank=True)  # e.g., ["English", "Spanish"]
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_talent'
    )
    
    class Meta:
        db_table = 'talent_pool'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_talent_type_display()})"


class CharacterTalentAssignment(models.Model):
    """Link voice actors to characters"""
    ROLE_TYPES = [
        ('voice_actor', 'Voice Actor'),
        ('motion_capture', 'Motion Capture'),
        ('reference_model', 'Reference Model'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('contacted', 'Contacted'),
        ('negotiating', 'Negotiating'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ]
    
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='talent_assignments')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='character_assignments')
    role_type = models.CharField(
        max_length=50,
        choices=ROLE_TYPES,
        default='voice_actor'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed'
    )
    rate_agreed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'character_talent_assignments'
        unique_together = ['character', 'talent', 'role_type']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.talent.name} → {self.character.name} ({self.get_role_type_display()})"


class AssetTalentAssignment(models.Model):
    """Link artists to assets"""
    ROLE_TYPES = [
        ('modeler', '3D Modeler'),
        ('texture_artist', 'Texture Artist'),
        ('rigger', 'Rigger'),
        ('concept_artist', 'Concept Artist'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('contacted', 'Contacted'),
        ('negotiating', 'Negotiating'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    asset = models.ForeignKey(StoryAsset, on_delete=models.CASCADE, related_name='talent_assignments')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='asset_assignments')
    role_type = models.CharField(
        max_length=50,
        choices=ROLE_TYPES,
        default='modeler'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed'
    )
    rate_agreed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_hours = models.IntegerField(null=True, blank=True)
    actual_hours = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'asset_talent_assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.talent.name} → {self.asset.name} ({self.get_role_type_display()})"


class ShotTalentAssignment(models.Model):
    """Link animators/specialists to shots"""
    ROLE_TYPES = [
        ('animator', 'Animator'),
        ('lighting_artist', 'Lighting Artist'),
        ('compositor', 'Compositor'),
        ('fx_artist', 'FX Artist'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('contacted', 'Contacted'),
        ('negotiating', 'Negotiating'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE, related_name='talent_assignments')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='shot_assignments')
    role_type = models.CharField(
        max_length=50,
        choices=ROLE_TYPES,
        default='animator'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed'
    )
    rate_agreed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_hours = models.IntegerField(null=True, blank=True)
    actual_hours = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shot_talent_assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.talent.name} → Shot {self.shot.shot_number} ({self.get_role_type_display()})"
