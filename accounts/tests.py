"""
Comprehensive Test Cases for User Management & Permissions System
Tests all endpoints for Users, Teams, Roles, Organizations, Invitations, and Story Access
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta

from .models import Organization, Team, Role, StoryAccess, Invitation
from ai_machines.models import Story

User = get_user_model()


class UserManagementAPITestCase(APITestCase):
    """Test cases for User CRUD operations"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client = APIClient()
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_list_users_success(self):
        """Test listing all users"""
        url = '/api/auth/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)  # Admin + test user
    
    def test_list_users_permission_denied(self):
        """Test that non-admin users cannot list all users"""
        # Create non-admin user
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(regular_user)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = '/api/auth/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_user_detail_success(self):
        """Test getting user details"""
        url = f'/api/auth/users/{self.test_user.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
    
    def test_get_user_detail_own_profile(self):
        """Test that users can view their own profile"""
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(regular_user)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = f'/api/auth/users/{regular_user.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_user_success(self):
        """Test updating user"""
        url = f'/api/auth/users/{self.test_user.id}/update/'
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, 'Updated')
        self.assertEqual(self.test_user.bio, 'Updated bio')
    
    def test_delete_user_success(self):
        """Test deleting user"""
        user_to_delete = User.objects.create_user(
            username='todelete',
            email='todelete@example.com',
            password='testpass123'
        )
        url = f'/api/auth/users/{user_to_delete.id}/delete/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=user_to_delete.id).exists())
    
    def test_delete_own_account_forbidden(self):
        """Test that users cannot delete their own account"""
        url = f'/api/auth/users/{self.user.id}/delete/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrganizationAPITestCase(APITestCase):
    """Test cases for Organization CRUD operations"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client = APIClient()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.organization = Organization.objects.create(name='Test Organization')
    
    def test_list_organizations_success(self):
        """Test listing organizations"""
        url = '/api/auth/organizations/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_create_organization_success(self):
        """Test creating organization"""
        url = '/api/auth/organizations/'
        data = {
            'name': 'New Organization'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Organization')
        self.assertEqual(Organization.objects.count(), 2)
    
    def test_get_organization_detail_success(self):
        """Test getting organization details"""
        url = f'/api/auth/organizations/{self.organization.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Organization')
    
    def test_update_organization_success(self):
        """Test updating organization"""
        url = f'/api/auth/organizations/{self.organization.id}/'
        data = {
            'name': 'Updated Organization'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.organization.refresh_from_db()
        self.assertEqual(self.organization.name, 'Updated Organization')
    
    def test_delete_organization_success(self):
        """Test deleting organization"""
        org_to_delete = Organization.objects.create(name='To Delete')
        url = f'/api/auth/organizations/{org_to_delete.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Organization.objects.filter(id=org_to_delete.id).exists())


class TeamAPITestCase(APITestCase):
    """Test cases for Team CRUD operations"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client = APIClient()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.organization = Organization.objects.create(name='Test Organization')
        self.team = Team.objects.create(
            name='Test Team',
            organization=self.organization,
            description='Test team description'
        )
    
    def test_list_teams_success(self):
        """Test listing teams"""
        url = '/api/auth/teams/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_create_team_success(self):
        """Test creating team"""
        url = '/api/auth/teams/'
        data = {
            'name': 'New Team',
            'organization': self.organization.id,
            'description': 'New team description'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Team')
        self.assertEqual(Team.objects.count(), 2)
    
    def test_get_team_detail_success(self):
        """Test getting team details"""
        url = f'/api/auth/teams/{self.team.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Team')
    
    def test_get_team_members_success(self):
        """Test getting team members"""
        # Add member to team
        member = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='testpass123'
        )
        member.team = self.team
        member.organization = self.organization
        member.save()
        
        url = f'/api/auth/teams/{self.team.id}/members/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'member@example.com')
    
    def test_add_team_member_success(self):
        """Test adding member to team"""
        member = User.objects.create_user(
            username='newmember',
            email='newmember@example.com',
            password='testpass123'
        )
        
        url = f'/api/auth/teams/{self.team.id}/members/'
        data = {
            'user_id': member.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        member.refresh_from_db()
        self.assertEqual(member.team, self.team)
        self.assertEqual(member.organization, self.organization)
    
    def test_remove_team_member_success(self):
        """Test removing member from team"""
        member = User.objects.create_user(
            username='toremove',
            email='toremove@example.com',
            password='testpass123'
        )
        member.team = self.team
        member.organization = self.organization
        member.save()
        
        url = f'/api/auth/teams/{self.team.id}/members/{member.id}/remove/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        member.refresh_from_db()
        self.assertIsNone(member.team)


class RoleAPITestCase(APITestCase):
    """Test cases for Role CRUD operations"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client = APIClient()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.role = Role.objects.create(
            name='Test Role',
            description='Test role description',
            permissions=['stories.view', 'stories.edit'],
            is_system_role=False
        )
    
    def test_list_roles_success(self):
        """Test listing roles"""
        url = '/api/auth/roles/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_create_role_success(self):
        """Test creating role"""
        url = '/api/auth/roles/'
        data = {
            'name': 'New Role',
            'description': 'New role description',
            'permissions': ['stories.view', 'assets.view'],
            'is_system_role': False
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Role')
        self.assertEqual(Role.objects.count(), 2)
    
    def test_get_role_detail_success(self):
        """Test getting role details"""
        url = f'/api/auth/roles/{self.role.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Role')
        self.assertEqual(len(response.data['permissions']), 2)
    
    def test_update_role_success(self):
        """Test updating role"""
        url = f'/api/auth/roles/{self.role.id}/'
        data = {
            'name': 'Updated Role',
            'permissions': ['stories.view', 'stories.edit', 'stories.delete']
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.role.refresh_from_db()
        self.assertEqual(self.role.name, 'Updated Role')
        self.assertEqual(len(self.role.permissions), 3)
    
    def test_update_system_role_forbidden(self):
        """Test that system roles cannot be modified"""
        system_role = Role.objects.create(
            name='System Role',
            is_system_role=True,
            permissions=['admin.settings']
        )
        
        url = f'/api/auth/roles/{system_role.id}/'
        data = {
            'name': 'Modified System Role'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_role_success(self):
        """Test deleting role"""
        role_to_delete = Role.objects.create(
            name='To Delete',
            is_system_role=False,
            permissions=[]
        )
        url = f'/api/auth/roles/{role_to_delete.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Role.objects.filter(id=role_to_delete.id).exists())
    
    def test_delete_system_role_forbidden(self):
        """Test that system roles cannot be deleted"""
        system_role = Role.objects.create(
            name='System Role',
            is_system_role=True,
            permissions=['admin.settings']
        )
        
        url = f'/api/auth/roles/{system_role.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class InvitationAPITestCase(APITestCase):
    """Test cases for Invitation operations"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client = APIClient()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.organization = Organization.objects.create(name='Test Organization')
        self.team = Team.objects.create(
            name='Test Team',
            organization=self.organization
        )
        self.role = Role.objects.create(
            name='Test Role',
            permissions=['stories.view']
        )
        
        self.invitation = Invitation.objects.create(
            email='invitee@example.com',
            organization=self.organization,
            team=self.team,
            role=self.role,
            invited_by=self.user,
            expires_at=timezone.now() + timedelta(days=7)
        )
    
    def test_list_invitations_success(self):
        """Test listing invitations"""
        url = '/api/auth/invitations/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_create_invitation_success(self):
        """Test creating invitation"""
        url = '/api/auth/invitations/'
        data = {
            'email': 'newinvitee@example.com',
            'organization': self.organization.id,
            'team': self.team.id,
            'role': self.role.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'newinvitee@example.com')
        self.assertIsNotNone(response.data['token'])
        self.assertEqual(Invitation.objects.count(), 2)
    
    def test_get_invitation_by_token_success(self):
        """Test getting invitation by token"""
        url = f'/api/auth/invitations/{self.invitation.token}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'invitee@example.com')
        self.assertEqual(response.data['status'], 'pending')
    
    def test_accept_invitation_success(self):
        """Test accepting invitation"""
        # Create user with matching email
        invitee = User.objects.create_user(
            username='invitee',
            email='invitee@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(invitee)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = f'/api/auth/invitations/{self.invitation.token}/accept/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, 'accepted')
        self.assertIsNotNone(self.invitation.accepted_at)
        
        invitee.refresh_from_db()
        self.assertEqual(invitee.organization, self.organization)
        self.assertEqual(invitee.team, self.team)
        self.assertEqual(invitee.role, self.role)
    
    def test_accept_invitation_email_mismatch(self):
        """Test that invitation can only be accepted by matching email"""
        # Create user with different email
        wrong_user = User.objects.create_user(
            username='wronguser',
            email='wrong@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(wrong_user)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = f'/api/auth/invitations/{self.invitation.token}/accept/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cancel_invitation_success(self):
        """Test cancelling invitation"""
        url = f'/api/auth/invitations/{self.invitation.id}/cancel/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, 'cancelled')


class StoryAccessAPITestCase(APITestCase):
    """Test cases for Story Access operations"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client = APIClient()
        
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.organization = Organization.objects.create(name='Test Organization')
        self.team = Team.objects.create(
            name='Test Team',
            organization=self.organization
        )
        
        self.story = Story.objects.create(
            user=self.user,
            title='Test Story',
            raw_text='Test content',
            parsed_data={}
        )
        
        self.access_user = User.objects.create_user(
            username='accessuser',
            email='accessuser@example.com',
            password='testpass123'
        )
    
    def test_list_story_access_success(self):
        """Test listing story access controls"""
        url = f'/api/auth/stories/{self.story.id}/access/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No access controls yet
    
    def test_create_story_access_user_success(self):
        """Test granting story access to user"""
        url = f'/api/auth/stories/{self.story.id}/access/'
        data = {
            'user': self.access_user.id,
            'can_view': True,
            'can_edit': True,
            'can_delete': False
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.access_user.id)
        self.assertTrue(response.data['can_view'])
        self.assertTrue(response.data['can_edit'])
        self.assertFalse(response.data['can_delete'])
        self.assertEqual(StoryAccess.objects.count(), 1)
    
    def test_create_story_access_team_success(self):
        """Test granting story access to team"""
        url = f'/api/auth/stories/{self.story.id}/access/'
        data = {
            'team': self.team.id,
            'can_view': True,
            'can_edit': False,
            'can_delete': False
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['team'], self.team.id)
        self.assertTrue(response.data['can_view'])
        self.assertEqual(StoryAccess.objects.count(), 1)
    
    def test_create_story_access_both_user_team_forbidden(self):
        """Test that cannot assign both user and team"""
        url = f'/api/auth/stories/{self.story.id}/access/'
        data = {
            'user': self.access_user.id,
            'team': self.team.id,
            'can_view': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_story_access_success(self):
        """Test updating story access"""
        access = StoryAccess.objects.create(
            story=self.story,
            user=self.access_user,
            can_view=True,
            can_edit=False,
            can_delete=False
        )
        
        url = f'/api/auth/stories/{self.story.id}/access/{access.id}/'
        data = {
            'can_view': True,
            'can_edit': True,
            'can_delete': True
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access.refresh_from_db()
        self.assertTrue(access.can_edit)
        self.assertTrue(access.can_delete)
    
    def test_delete_story_access_success(self):
        """Test revoking story access"""
        access = StoryAccess.objects.create(
            story=self.story,
            user=self.access_user,
            can_view=True
        )
        
        url = f'/api/auth/stories/{self.story.id}/access/{access.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StoryAccess.objects.count(), 0)


class PermissionTestCase(TestCase):
    """Test cases for permission checking"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.role = Role.objects.create(
            name='Test Role',
            permissions=['stories.view', 'stories.edit']
        )
        
        self.user.role = self.role
        self.user.save()
        
        self.story = Story.objects.create(
            user=self.user,
            title='Test Story',
            raw_text='Test content',
            parsed_data={}
        )
    
    def test_user_has_permission(self):
        """Test user has permission check"""
        self.assertTrue(self.user.has_permission('stories.view'))
        self.assertTrue(self.user.has_permission('stories.edit'))
        self.assertFalse(self.user.has_permission('stories.delete'))
    
    def test_superuser_has_all_permissions(self):
        """Test that superuser has all permissions"""
        self.user.is_superuser = True
        self.user.save()
        
        self.assertTrue(self.user.has_permission('stories.view'))
        self.assertTrue(self.user.has_permission('stories.delete'))
        self.assertTrue(self.user.has_permission('admin.settings'))
    
    def test_story_access_check(self):
        """Test story access checking"""
        # User owns the story, should have access
        self.assertTrue(self.user.has_resource_access(self.story))
        
        # Create another user
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        
        # Other user should not have access
        self.assertFalse(other_user.has_resource_access(self.story))
        
        # Grant access
        StoryAccess.objects.create(
            story=self.story,
            user=other_user,
            can_view=True
        )
        
        # Now should have access
        self.assertTrue(other_user.has_resource_access(self.story))
