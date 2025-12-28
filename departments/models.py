from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Department(models.Model):
    """Production department/workspace"""
    DEPARTMENT_TYPES = [
        # Core departments
        ('concept_art', 'Concept Art'),
        ('modeling', 'Modeling'),
        ('texturing', 'Texturing'),
        ('rigging', 'Rigging'),
        ('animation', 'Animation'),
        ('programming', 'Programming/Technology'),
        ('effects', 'Effects'),
        ('lighting_rendering', 'Lighting and Rendering'),
        ('farm', 'Farm'),
        # Additional departments
        ('previs', 'Previs (Pre-visualization)'),
        ('story_script', 'Story/Script'),
        ('pre_production', 'Pre-Production'),
        ('post_production', 'Post-Production'),
        ('audio_sound', 'Audio/Sound'),
        ('qa', 'Quality Assurance'),
        ('project_management', 'Project Management'),
        ('art_direction', 'Art Direction'),
        ('environment_design', 'Environment Design'),
        ('character_design', 'Character Design'),
        ('asset_management', 'Asset Management'),
        ('layout', 'Layout'),
        ('compositing', 'Compositing'),
        ('review_approval', 'Review/Approval'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=100)
    department_type = models.CharField(max_length=50, choices=DEPARTMENT_TYPES, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon name/emoji
    
    # Color coding
    color = models.CharField(max_length=7, default='#1976d2')  # Hex color
    
    # Settings
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)  # For sorting
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class StoryDepartment(models.Model):
    """Link departments to stories (workspace assignment)"""
    story = models.ForeignKey('ai_machines.Story', on_delete=models.CASCADE, related_name='story_departments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='stories')
    
    # Department-specific settings for this story
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'story_departments'
        unique_together = ['story', 'department']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.story.title} - {self.department.name}"


class AssetDepartmentAssignment(models.Model):
    """Assign assets to departments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    asset = models.ForeignKey('ai_machines.StoryAsset', on_delete=models.CASCADE, related_name='department_assignments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='asset_assignments')
    
    # Assignment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'asset_department_assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.asset.name} - {self.department.name}"


class ShotDepartmentAssignment(models.Model):
    """Assign shots to departments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    shot = models.ForeignKey('ai_machines.Shot', on_delete=models.CASCADE, related_name='department_assignments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='shot_assignments')
    
    # Assignment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shot_department_assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"Shot {self.shot.shot_number} - {self.department.name}"
