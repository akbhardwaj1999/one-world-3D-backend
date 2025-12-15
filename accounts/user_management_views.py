from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Organization, Team, Role, StoryAccess, Invitation
from .serializers import (
    UserSerializer, OrganizationSerializer, TeamSerializer, RoleSerializer,
    StoryAccessSerializer, InvitationSerializer
)


# ==================== User Management Views ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_list(request):
    """List all users"""
    # Allow staff, users with admin.users permission, or users can see their organization's users
    if request.user.is_staff or request.user.has_permission('admin.users'):
        users = User.objects.all()
    elif request.user.organization:
        # Users can see users from their own organization
        users = User.objects.filter(organization=request.user.organization)
    else:
        # If no organization, only show own profile
        users = User.objects.filter(id=request.user.id)
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_detail(request, pk):
    """Get user details"""
    try:
        user = User.objects.get(pk=pk)
        # Users can view their own profile, admins can view any
        if user != request.user and not request.user.is_staff and not request.user.has_permission('admin.users'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def user_update(request, pk):
    """Update user"""
    try:
        user = User.objects.get(pk=pk)
        # Users can update their own profile, admins can update any
        if user != request.user and not request.user.is_staff and not request.user.has_permission('admin.users'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_delete(request, pk):
    """Delete user (Admin only)"""
    if not request.user.is_staff and not request.user.has_permission('admin.users'):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(pk=pk)
        if user == request.user:
            return Response({'error': 'Cannot delete your own account'}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== Organization Views ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def organization_list_create(request):
    """List or create organizations"""
    if request.method == 'GET':
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Allow any authenticated user to create organizations (for initial setup)
        # In production, you might want to restrict this to admins only
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def organization_detail(request, pk):
    """Get, update, or delete organization"""
    try:
        organization = Organization.objects.get(pk=pk)
        
        if request.method == 'GET':
            serializer = OrganizationSerializer(organization)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            if not request.user.is_staff and not request.user.has_permission('admin.settings'):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = OrganizationSerializer(organization, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            if not request.user.is_staff and not request.user.has_permission('admin.settings'):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            organization.delete()
            return Response({'message': 'Organization deleted successfully'}, status=status.HTTP_200_OK)
    
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== Team Views ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def team_list_create(request):
    """List or create teams"""
    if request.method == 'GET':
        # Filter by organization if user has one
        teams = Team.objects.all()
        if request.user.organization:
            teams = teams.filter(organization=request.user.organization)
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Allow any authenticated user to create teams (for initial setup)
        # In production, you might want to restrict this to admins or users with admin.teams permission
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def team_detail(request, pk):
    """Get, update, or delete team"""
    try:
        team = Team.objects.get(pk=pk)
        
        if request.method == 'GET':
            serializer = TeamSerializer(team)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            if not request.user.is_staff and not request.user.has_permission('admin.teams'):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = TeamSerializer(team, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            if not request.user.is_staff and not request.user.has_permission('admin.teams'):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            team.delete()
            return Response({'message': 'Team deleted successfully'}, status=status.HTTP_200_OK)
    
    except Team.DoesNotExist:
        return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def team_members(request, pk):
    """Get or add team members"""
    try:
        team = Team.objects.get(pk=pk)
        
        if request.method == 'GET':
            members = team.members.all()
            serializer = UserSerializer(members, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            if not request.user.is_staff and not request.user.has_permission('admin.teams'):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(pk=user_id)
                user.team = team
                user.organization = team.organization
                user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Team.DoesNotExist:
        return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def team_member_remove(request, pk, user_id):
    """Remove member from team"""
    if not request.user.is_staff and not request.user.has_permission('admin.teams'):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        team = Team.objects.get(pk=pk)
        user = User.objects.get(pk=user_id)
        
        if user.team == team:
            user.team = None
            user.save()
            return Response({'message': 'Member removed from team'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not a member of this team'}, status=status.HTTP_400_BAD_REQUEST)
    
    except (Team.DoesNotExist, User.DoesNotExist):
        return Response({'error': 'Team or user not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== Role Views ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def role_list_create(request):
    """List or create roles"""
    if request.method == 'GET':
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Allow any authenticated user to create roles (for initial setup)
        # In production, you might want to restrict this to admins or users with admin.roles permission
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def role_detail(request, pk):
    """Get, update, or delete role"""
    try:
        role = Role.objects.get(pk=pk)
        
        if request.method == 'GET':
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            # Allow any authenticated user to update roles (for testing purposes)
            # In production, you might want to restrict system roles or add permission checks
            serializer = RoleSerializer(role, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            if not request.user.is_staff and not request.user.has_permission('admin.roles'):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            if role.is_system_role:
                return Response({'error': 'Cannot delete system roles'}, status=status.HTTP_400_BAD_REQUEST)
            
            role.delete()
            return Response({'message': 'Role deleted successfully'}, status=status.HTTP_200_OK)
    
    except Role.DoesNotExist:
        return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== Invitation Views ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def invitation_list_create(request):
    """List or create invitations"""
    if request.method == 'GET':
        invitations = Invitation.objects.all()
        # Filter by organization if user has one
        if request.user.organization:
            invitations = invitations.filter(organization=request.user.organization)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_staff and not request.user.has_permission('admin.users'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = InvitationSerializer(data=request.data)
        if serializer.is_valid():
            invitation = serializer.save(
                invited_by=request.user,
                expires_at=timezone.now() + timedelta(days=7)
            )
            
            # Send invitation email
            try:
                invite_url = f"{settings.FRONTEND_URL}/accept-invitation/{invitation.token}/"
                send_mail(
                    subject=f'Invitation to join {invitation.team.name} - ONE WORLD 3D',
                    message=f'''
Hello,

You've been invited by {request.user.get_full_name() or request.user.email} to join {invitation.team.name} on ONE WORLD 3D.

Your role: {invitation.role.name}

Click here to accept: {invite_url}

This invitation expires in 7 days.

If you didn't expect this invitation, you can ignore this email.

Best regards,
ONE WORLD 3D Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[invitation.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"[INVITATION EMAIL ERROR] Failed to send email: {str(e)}")
                # Continue even if email fails
            
            return Response(InvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def invitation_detail(request, token):
    """Get invitation by token"""
    try:
        invitation = Invitation.objects.get(token=token)
        
        if invitation.status != 'pending':
            return Response({'error': 'Invitation is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        if invitation.is_expired():
            invitation.status = 'expired'
            invitation.save()
            return Response({'error': 'Invitation has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = InvitationSerializer(invitation)
        return Response(serializer.data)
    
    except Invitation.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def invitation_accept(request, token):
    """Accept invitation"""
    try:
        invitation = Invitation.objects.get(token=token)
        
        if invitation.status != 'pending':
            return Response({'error': 'Invitation is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        if invitation.is_expired():
            invitation.status = 'expired'
            invitation.save()
            return Response({'error': 'Invitation has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify email matches
        if request.user.email != invitation.email:
            return Response({'error': 'Email does not match invitation'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Add user to team and organization
        request.user.organization = invitation.organization
        request.user.team = invitation.team
        request.user.role = invitation.role
        request.user.save()
        
        # Update invitation
        invitation.status = 'accepted'
        invitation.accepted_at = timezone.now()
        invitation.save()
        
        return Response({
            'message': 'Invitation accepted successfully',
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    
    except Invitation.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def invitation_cancel(request, pk):
    """Cancel invitation"""
    if not request.user.is_staff and not request.user.has_permission('admin.users'):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        invitation = Invitation.objects.get(pk=pk)
        
        if invitation.status != 'pending':
            return Response({'error': 'Can only cancel pending invitations'}, status=status.HTTP_400_BAD_REQUEST)
        
        invitation.status = 'cancelled'
        invitation.save()
        
        return Response({'message': 'Invitation cancelled successfully'}, status=status.HTTP_200_OK)
    
    except Invitation.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== Story Access Views ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def story_access_list_create(request, story_id):
    """Get or create story access controls"""
    from ai_machines.models import Story
    
    try:
        story = Story.objects.get(pk=story_id)
        
        # Check if user has permission to manage story access
        if not story.user == request.user and not request.user.is_staff and not request.user.has_permission('admin.settings'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            accesses = StoryAccess.objects.filter(story=story)
            serializer = StoryAccessSerializer(accesses, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = StoryAccessSerializer(data={
                **request.data,
                'story': story_id
            })
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Story.DoesNotExist:
        return Response({'error': 'Story not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def story_access_detail(request, story_id, access_id):
    """Update or delete story access"""
    from ai_machines.models import Story
    
    try:
        story = Story.objects.get(pk=story_id)
        access = StoryAccess.objects.get(pk=access_id, story=story)
        
        # Check permission
        if not story.user == request.user and not request.user.is_staff and not request.user.has_permission('admin.settings'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method in ['PUT', 'PATCH']:
            serializer = StoryAccessSerializer(access, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            access.delete()
            return Response({'message': 'Access revoked successfully'}, status=status.HTTP_200_OK)
    
    except (Story.DoesNotExist, StoryAccess.DoesNotExist):
        return Response({'error': 'Story or access not found'}, status=status.HTTP_404_NOT_FOUND)

