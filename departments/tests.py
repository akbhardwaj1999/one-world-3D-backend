"""
Comprehensive Test Cases for Department Management System
Tests all endpoints for Departments, Story Departments, Asset/Shot Assignments
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta

from .models import Department, StoryDepartment, AssetDepartmentAssignment, ShotDepartmentAssignment
from ai_machines.models import Story, StoryAsset, Shot, Sequence, Location, Character

User = get_user_model()


class DepartmentAPITestCase(APITestCase):
    """Test cases for Department CRUD operations"""
    
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
        
        # Create test department
        self.test_department = Department.objects.create(
            name='Test Modeling',
            department_type='modeling',
            description='Test modeling department',
            icon='🏗️',
            color='#2196F3',
            is_active=True,
            display_order=1
        )
    
    def test_list_departments_success(self):
        """Test listing all active departments"""
        url = '/api/departments/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Modeling')
    
    def test_create_department_success(self):
        """Test creating a new department"""
        url = '/api/departments/'
        data = {
            'name': 'Animation Department',
            'department_type': 'animation',
            'description': 'Character animation department',
            'icon': '🎬',
            'color': '#00BCD4',
            'is_active': True,
            'display_order': 2
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Animation Department')
        self.assertEqual(response.data['department_type'], 'animation')
        self.assertTrue(Department.objects.filter(name='Animation Department').exists())
    
    def test_create_department_duplicate_type(self):
        """Test that duplicate department types are not allowed"""
        url = '/api/departments/'
        data = {
            'name': 'Another Modeling',
            'department_type': 'modeling',  # Same as existing
            'description': 'Another modeling department',
            'icon': '🏗️',
            'color': '#2196F3',
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_department_detail_success(self):
        """Test getting department details"""
        url = f'/api/departments/{self.test_department.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Modeling')
        self.assertEqual(response.data['department_type'], 'modeling')
        self.assertEqual(response.data['assets_count'], 0)
        self.assertEqual(response.data['shots_count'], 0)
    
    def test_update_department_success(self):
        """Test updating a department"""
        url = f'/api/departments/{self.test_department.id}/'
        data = {
            'name': 'Updated Modeling',
            'description': 'Updated description',
            'color': '#FF0000'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Modeling')
        self.assertEqual(response.data['color'], '#FF0000')
        
        # Verify in database
        self.test_department.refresh_from_db()
        self.assertEqual(self.test_department.name, 'Updated Modeling')
    
    def test_partial_update_department_success(self):
        """Test partial update of a department"""
        url = f'/api/departments/{self.test_department.id}/'
        data = {
            'is_active': False
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])
        
        # Verify in database
        self.test_department.refresh_from_db()
        self.assertFalse(self.test_department.is_active)
    
    def test_delete_department_success(self):
        """Test deleting a department"""
        dept_id = self.test_department.id
        url = f'/api/departments/{dept_id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Department.objects.filter(id=dept_id).exists())
    
    def test_department_requires_authentication(self):
        """Test that department endpoints require authentication"""
        self.client.credentials()  # Remove authentication
        url = '/api/departments/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StoryDepartmentAPITestCase(APITestCase):
    """Test cases for Story Department assignments"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test story
        self.story = Story.objects.create(
            user=self.user,
            title='Test Story',
            raw_text='Test story content',
            parsed_data={}
        )
        
        # Create test departments
        self.department1 = Department.objects.create(
            name='Modeling',
            department_type='modeling',
            description='3D modeling',
            icon='🏗️',
            color='#2196F3'
        )
        self.department2 = Department.objects.create(
            name='Animation',
            department_type='animation',
            description='Animation',
            icon='🎬',
            color='#00BCD4'
        )
    
    def test_list_story_departments_success(self):
        """Test listing departments for a story"""
        # Create a story department assignment
        StoryDepartment.objects.create(
            story=self.story,
            department=self.department1,
            assigned_by=self.user
        )
        
        url = f'/api/departments/stories/{self.story.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['department_name'], 'Modeling')
    
    def test_assign_department_to_story_success(self):
        """Test assigning a department to a story"""
        url = f'/api/departments/stories/{self.story.id}/'
        data = {
            'department': self.department1.id,
            'notes': 'Initial assignment'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['department_name'], 'Modeling')
        self.assertTrue(StoryDepartment.objects.filter(
            story=self.story,
            department=self.department1
        ).exists())
    
    def test_assign_duplicate_department_to_story(self):
        """Test that duplicate department assignments are not allowed"""
        # Create existing assignment
        StoryDepartment.objects.create(
            story=self.story,
            department=self.department1,
            assigned_by=self.user
        )
        
        url = f'/api/departments/stories/{self.story.id}/'
        data = {
            'department': self.department1.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already assigned', response.data['error'].lower())
    
    def test_remove_department_from_story_success(self):
        """Test removing a department from a story"""
        # Create assignment
        StoryDepartment.objects.create(
            story=self.story,
            department=self.department1,
            assigned_by=self.user
        )
        
        url = f'/api/departments/stories/{self.story.id}/{self.department1.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(StoryDepartment.objects.filter(
            story=self.story,
            department=self.department1
        ).exists())
    
    def test_story_departments_permission_check(self):
        """Test that users can only access their own stories"""
        # Create another user and story
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        other_story = Story.objects.create(
            user=other_user,
            title='Other Story',
            raw_text='Other content',
            parsed_data={}
        )
        
        url = f'/api/departments/stories/{other_story.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AssetDepartmentAssignmentAPITestCase(APITestCase):
    """Test cases for Asset Department assignments"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test story and asset
        self.story = Story.objects.create(
            user=self.user,
            title='Test Story',
            raw_text='Test story content',
            parsed_data={}
        )
        self.asset = StoryAsset.objects.create(
            story=self.story,
            name='Test Asset',
            asset_type='model',
            description='Test asset description'
        )
        
        # Create test department
        self.department = Department.objects.create(
            name='Modeling',
            department_type='modeling',
            description='3D modeling',
            icon='🏗️',
            color='#2196F3'
        )
    
    def test_list_asset_department_assignments_success(self):
        """Test listing department assignments for an asset"""
        # Create assignment
        AssetDepartmentAssignment.objects.create(
            asset=self.asset,
            department=self.department,
            status='in_progress',
            priority='high',
            assigned_by=self.user
        )
        
        url = f'/api/departments/stories/{self.story.id}/assets/{self.asset.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'in_progress')
        self.assertEqual(response.data[0]['priority'], 'high')
    
    def test_create_asset_department_assignment_success(self):
        """Test creating an asset department assignment"""
        url = f'/api/departments/stories/{self.story.id}/assets/{self.asset.id}/'
        data = {
            'department': self.department.id,
            'status': 'pending',
            'priority': 'medium',
            'notes': 'Initial assignment'
        }
        response = self.client.post(url, data, format='json')
        
        # Check if it was created or updated (if already exists)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        if response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]:
            self.assertEqual(response.data['status'], 'pending')
            self.assertEqual(response.data['priority'], 'medium')
            self.assertTrue(AssetDepartmentAssignment.objects.filter(
                asset=self.asset,
                department=self.department
            ).exists())
    
    def test_update_existing_asset_assignment(self):
        """Test that posting to existing assignment updates it"""
        # Create existing assignment
        assignment = AssetDepartmentAssignment.objects.create(
            asset=self.asset,
            department=self.department,
            status='pending',
            assigned_by=self.user
        )
        
        url = f'/api/departments/stories/{self.story.id}/assets/{self.asset.id}/'
        data = {
            'department': self.department.id,
            'status': 'in_progress',
            'priority': 'high'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'in_progress')
        self.assertEqual(assignment.priority, 'high')
    
    def test_update_asset_assignment_detail_success(self):
        """Test updating an asset assignment"""
        assignment = AssetDepartmentAssignment.objects.create(
            asset=self.asset,
            department=self.department,
            status='pending',
            assigned_by=self.user
        )
        
        url = f'/api/departments/assignments/asset/{assignment.id}/'
        data = {
            'status': 'completed',
            'priority': 'low',
            'notes': 'Work completed'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'completed')
    
    def test_delete_asset_assignment_success(self):
        """Test deleting an asset assignment"""
        assignment = AssetDepartmentAssignment.objects.create(
            asset=self.asset,
            department=self.department,
            assigned_by=self.user
        )
        
        url = f'/api/departments/assignments/asset/{assignment.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(AssetDepartmentAssignment.objects.filter(id=assignment.id).exists())
    
    def test_asset_assignment_permission_check(self):
        """Test that users can only access their own story assets"""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        other_story = Story.objects.create(
            user=other_user,
            title='Other Story',
            raw_text='Other content',
            parsed_data={}
        )
        other_asset = StoryAsset.objects.create(
            story=other_story,
            name='Other Asset',
            asset_type='model'
        )
        
        url = f'/api/departments/stories/{other_story.id}/assets/{other_asset.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ShotDepartmentAssignmentAPITestCase(APITestCase):
    """Test cases for Shot Department assignments"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test story and shot
        self.story = Story.objects.create(
            user=self.user,
            title='Test Story',
            raw_text='Test story content',
            parsed_data={}
        )
        self.location = Location.objects.create(
            story=self.story,
            name='Test Location',
            description='Test location'
        )
        self.sequence = Sequence.objects.create(
            story=self.story,
            sequence_number=1,
            title='Test Sequence',
            location=self.location
        )
        self.shot = Shot.objects.create(
            story=self.story,
            sequence=self.sequence,
            shot_number=1,
            description='Test shot description'
        )
        
        # Create test department
        self.department = Department.objects.create(
            name='Animation',
            department_type='animation',
            description='Animation',
            icon='🎬',
            color='#00BCD4'
        )
    
    def test_list_shot_department_assignments_success(self):
        """Test listing department assignments for a shot"""
        # Create assignment
        ShotDepartmentAssignment.objects.create(
            shot=self.shot,
            department=self.department,
            status='in_progress',
            priority='high',
            assigned_by=self.user
        )
        
        url = f'/api/departments/stories/{self.story.id}/shots/{self.shot.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'in_progress')
        self.assertEqual(response.data[0]['shot_number'], 1)
    
    def test_create_shot_department_assignment_success(self):
        """Test creating a shot department assignment"""
        url = f'/api/departments/stories/{self.story.id}/shots/{self.shot.id}/'
        # Format due_date properly for Django REST Framework
        due_date = timezone.now() + timedelta(days=7)
        data = {
            'department': self.department.id,
            'status': 'pending',
            'priority': 'medium',
            'due_date': due_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'notes': 'Initial assignment'
        }
        response = self.client.post(url, data, format='json')
        
        # Check if it was created or updated (if already exists)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        self.assertEqual(response.data['status'], 'pending')
        self.assertTrue(ShotDepartmentAssignment.objects.filter(
            shot=self.shot,
            department=self.department
        ).exists())
    
    def test_update_shot_assignment_detail_success(self):
        """Test updating a shot assignment"""
        assignment = ShotDepartmentAssignment.objects.create(
            shot=self.shot,
            department=self.department,
            status='pending',
            assigned_by=self.user
        )
        
        url = f'/api/departments/assignments/shot/{assignment.id}/'
        data = {
            'status': 'completed',
            'priority': 'low'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'completed')
    
    def test_delete_shot_assignment_success(self):
        """Test deleting a shot assignment"""
        assignment = ShotDepartmentAssignment.objects.create(
            shot=self.shot,
            department=self.department,
            assigned_by=self.user
        )
        
        url = f'/api/departments/assignments/shot/{assignment.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ShotDepartmentAssignment.objects.filter(id=assignment.id).exists())


class DepartmentStatsAPITestCase(APITestCase):
    """Test cases for Department statistics"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test story
        self.story = Story.objects.create(
            user=self.user,
            title='Test Story',
            raw_text='Test story content',
            parsed_data={}
        )
        
        # Create test department
        self.department = Department.objects.create(
            name='Modeling',
            department_type='modeling',
            description='3D modeling',
            icon='🏗️',
            color='#2196F3'
        )
        
        # Create test assets and shots
        self.asset1 = StoryAsset.objects.create(
            story=self.story,
            name='Asset 1',
            asset_type='model'
        )
        self.asset2 = StoryAsset.objects.create(
            story=self.story,
            name='Asset 2',
            asset_type='prop'
        )
        
        self.location = Location.objects.create(
            story=self.story,
            name='Test Location'
        )
        self.sequence = Sequence.objects.create(
            story=self.story,
            sequence_number=1,
            location=self.location
        )
        self.shot1 = Shot.objects.create(
            story=self.story,
            sequence=self.sequence,
            shot_number=1,
            description='Shot 1'
        )
        self.shot2 = Shot.objects.create(
            story=self.story,
            sequence=self.sequence,
            shot_number=2,
            description='Shot 2'
        )
        
        # Create assignments with different statuses
        AssetDepartmentAssignment.objects.create(
            asset=self.asset1,
            department=self.department,
            status='pending',
            priority='high',
            assigned_by=self.user
        )
        AssetDepartmentAssignment.objects.create(
            asset=self.asset2,
            department=self.department,
            status='completed',
            priority='medium',
            assigned_by=self.user
        )
        ShotDepartmentAssignment.objects.create(
            shot=self.shot1,
            department=self.department,
            status='in_progress',
            priority='high',
            assigned_by=self.user
        )
        ShotDepartmentAssignment.objects.create(
            shot=self.shot2,
            department=self.department,
            status='review',
            priority='low',
            assigned_by=self.user
        )
    
    def test_department_stats_success(self):
        """Test getting department statistics"""
        url = f'/api/departments/stories/{self.story.id}/{self.department.id}/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['department']['name'], 'Modeling')
        self.assertEqual(response.data['assets']['total'], 2)
        self.assertEqual(response.data['shots']['total'], 2)
        self.assertEqual(response.data['assets']['by_status']['pending'], 1)
        self.assertEqual(response.data['assets']['by_status']['completed'], 1)
        self.assertEqual(response.data['shots']['by_status']['in_progress'], 1)
        self.assertEqual(response.data['shots']['by_status']['review'], 1)
    
    def test_department_assets_list_success(self):
        """Test getting all assets for a department"""
        url = f'/api/departments/stories/{self.story.id}/{self.department.id}/assets/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Check that both assets are in the response (order may vary)
        asset_names = [item['asset_name'] for item in response.data]
        self.assertIn('Asset 1', asset_names)
        self.assertIn('Asset 2', asset_names)
    
    def test_department_shots_list_success(self):
        """Test getting all shots for a department"""
        url = f'/api/departments/stories/{self.story.id}/{self.department.id}/shots/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['shot_number'], 1)


class DepartmentModelTestCase(TestCase):
    """Test cases for Department models"""
    
    def test_department_str_representation(self):
        """Test department string representation"""
        dept = Department.objects.create(
            name='Test Department',
            department_type='modeling'
        )
        self.assertEqual(str(dept), 'Test Department')
    
    def test_story_department_str_representation(self):
        """Test story department string representation"""
        user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='testpass123'
        )
        story = Story.objects.create(
            user=user,
            title='Test Story',
            raw_text='Content',
            parsed_data={}
        )
        dept = Department.objects.create(
            name='Modeling',
            department_type='modeling'
        )
        story_dept = StoryDepartment.objects.create(
            story=story,
            department=dept,
            assigned_by=user
        )
        self.assertEqual(str(story_dept), 'Test Story - Modeling')
    
    def test_asset_assignment_str_representation(self):
        """Test asset assignment string representation"""
        user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='testpass123'
        )
        story = Story.objects.create(
            user=user,
            title='Test Story',
            raw_text='Content',
            parsed_data={}
        )
        asset = StoryAsset.objects.create(
            story=story,
            name='Test Asset',
            asset_type='model'
        )
        dept = Department.objects.create(
            name='Modeling',
            department_type='modeling'
        )
        assignment = AssetDepartmentAssignment.objects.create(
            asset=asset,
            department=dept,
            assigned_by=user
        )
        self.assertEqual(str(assignment), 'Test Asset - Modeling')
    
    def test_shot_assignment_str_representation(self):
        """Test shot assignment string representation"""
        user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='testpass123'
        )
        story = Story.objects.create(
            user=user,
            title='Test Story',
            raw_text='Content',
            parsed_data={}
        )
        location = Location.objects.create(
            story=story,
            name='Test Location'
        )
        sequence = Sequence.objects.create(
            story=story,
            sequence_number=1,
            location=location
        )
        shot = Shot.objects.create(
            story=story,
            sequence=sequence,
            shot_number=5,
            description='Test shot'
        )
        dept = Department.objects.create(
            name='Animation',
            department_type='animation'
        )
        assignment = ShotDepartmentAssignment.objects.create(
            shot=shot,
            department=dept,
            assigned_by=user
        )
        self.assertEqual(str(assignment), 'Shot 5 - Animation')
    
    def test_department_ordering(self):
        """Test that departments are ordered by display_order and name"""
        dept1 = Department.objects.create(
            name='B Department',
            department_type='modeling',
            display_order=2
        )
        dept2 = Department.objects.create(
            name='A Department',
            department_type='animation',
            display_order=1
        )
        dept3 = Department.objects.create(
            name='C Department',
            department_type='texturing',
            display_order=2
        )
        
        departments = list(Department.objects.all())
        self.assertEqual(departments[0], dept2)  # display_order=1
        self.assertEqual(departments[1], dept1)  # display_order=2, name='B'
        self.assertEqual(departments[2], dept3)  # display_order=2, name='C'
