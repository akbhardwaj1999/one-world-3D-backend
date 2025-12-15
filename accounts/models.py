from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets


class Organization(models.Model):
    """Organization/Company"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')
        super().save(*args, **kwargs)


class Team(models.Model):
    """Team within organization"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class Role(models.Model):
    """User role with permissions"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)  # Can't be deleted
    
    # Permissions (stored as JSON array)
    permissions = models.JSONField(default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """Extended user model"""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Organization & Team
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    # Profile
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email or self.username
    
    def has_permission(self, permission, resource=None):
        """Check if user has permission"""
        if self.is_superuser:
            return True
        
        if self.role and permission in self.role.permissions:
            if resource:
                return self.has_resource_access(resource)
            return True
        
        return False
    
    def has_resource_access(self, resource):
        """Check resource access"""
        # Check if user is superuser
        if self.is_superuser:
            return True
        
        # Check story access
        if hasattr(resource, 'story'):
            resource = resource.story
        
        # Import here to avoid circular import
        from .models import StoryAccess
        
        if hasattr(resource, 'access_controls'):
            # Check direct user access
            if StoryAccess.objects.filter(story=resource, user=self).exists():
                return True
            
            # Check team access
            if self.team:
                if StoryAccess.objects.filter(story=resource, team=self.team).exists():
                    return True
        
        # Check if user owns the story
        if hasattr(resource, 'user') and resource.user == self:
            return True
        
        # Check team ownership
        if self.team and hasattr(resource, 'team') and resource.team == self.team:
            return True
        
        return False


class StoryAccess(models.Model):
    """Control access to specific stories"""
    story = models.ForeignKey('ai_machines.Story', on_delete=models.CASCADE, related_name='access_controls')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_accesses', null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='story_accesses', null=True, blank=True)
    
    # Access level
    can_view = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'story_access'
        unique_together = [['story', 'user'], ['story', 'team']]
        verbose_name = 'Story Access'
        verbose_name_plural = 'Story Access Controls'
    
    def __str__(self):
        if self.user:
            return f"{self.story.title} - {self.user.username}"
        return f"{self.story.title} - {self.team.name}"


class Invitation(models.Model):
    """Team invitation"""
    email = models.EmailField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    # Invitation details
    token = models.CharField(max_length=64, unique=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'invitations'
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'
    
    def __str__(self):
        return f"Invitation to {self.email} - {self.team.name}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if invitation is expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
