"""
Permission checking utilities and decorators
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def has_permission(permission, resource=None):
    """
    Check if user has permission
    
    Usage:
        if has_permission(user, 'stories.edit', story):
            # User can edit this story
    """
    if not hasattr(permission, '__call__'):
        # If permission is a string, create a function
        def check(user, resource=None):
            return user.has_permission(permission, resource)
        return check
    return permission


def require_permission(permission):
    """
    Decorator to require permission for a view
    
    Usage:
        @require_permission('stories.edit')
        def edit_story(request, story_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get resource if needed (e.g., story_id from kwargs)
            resource = None
            if 'story_id' in kwargs:
                from ai_machines.models import Story
                try:
                    resource = Story.objects.get(pk=kwargs['story_id'])
                except Story.DoesNotExist:
                    return Response(
                        {'error': 'Story not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Check permission
            if not request.user.has_permission(permission, resource):
                return Response(
                    {'error': 'Permission denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_story_access(user, story, permission='stories.view'):
    """
    Check if user has access to a story
    
    Args:
        user: User instance
        story: Story instance
        permission: Permission to check (default: 'stories.view')
    
    Returns:
        bool: True if user has access, False otherwise
    """
    # Superuser has all access
    if user.is_superuser:
        return True
    
    # Story owner has all access
    if story.user == user:
        return True
    
    # Check role permission
    if not user.has_permission(permission):
        return False
    
    # Check story access controls
    from .models import StoryAccess
    
    # Check direct user access
    user_access = StoryAccess.objects.filter(story=story, user=user).first()
    if user_access:
        if permission == 'stories.view' and user_access.can_view:
            return True
        if permission == 'stories.edit' and user_access.can_edit:
            return True
        if permission == 'stories.delete' and user_access.can_delete:
            return True
    
    # Check team access
    if user.team:
        team_access = StoryAccess.objects.filter(story=story, team=user.team).first()
        if team_access:
            if permission == 'stories.view' and team_access.can_view:
                return True
            if permission == 'stories.edit' and team_access.can_edit:
                return True
            if permission == 'stories.delete' and team_access.can_delete:
                return True
    
    # Check if user's team matches story's team (if story has team)
    if hasattr(story, 'team') and story.team and user.team == story.team:
        return True
    
    return False


def check_resource_access(user, resource, permission):
    """
    Generic resource access checker
    
    Args:
        user: User instance
        resource: Resource instance (Story, Asset, Shot, etc.)
        permission: Permission string (e.g., 'stories.view', 'assets.edit')
    
    Returns:
        bool: True if user has access, False otherwise
    """
    # Superuser has all access
    if user.is_superuser:
        return True
    
    # Check if resource has a story (for assets/shots)
    if hasattr(resource, 'story'):
        return check_story_access(user, resource.story, permission)
    
    # Check if resource is a story
    if hasattr(resource, 'user'):
        return check_story_access(user, resource, permission)
    
    # Default: check role permission
    return user.has_permission(permission)

