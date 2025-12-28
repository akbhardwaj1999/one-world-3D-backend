"""
Django management command to create dummy data for User Management testing
Creates: Organizations, Teams, Roles, Users, and Invitations
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets
import random

from accounts.models import Organization, Team, Role, Invitation

User = get_user_model()


class Command(BaseCommand):
    help = 'Create dummy data for User Management testing (20 of each)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of items to create for each type (default: 20)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(self.style.SUCCESS('\nCreating dummy data for User Management...\n'))
        
        # Create or get superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@oneworld3d.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Created admin user: {admin_user.email}'))
        else:
            self.stdout.write(self.style.WARNING(f'[SKIP] Admin user already exists: {admin_user.email}'))
        
        # Get or create default roles
        default_roles = []
        role_names = ['Super Admin', 'Admin', 'Project Manager', 'Artist/Contractor', 'Reviewer', 'Viewer']
        for role_name in role_names:
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={
                    'description': f'Default {role_name} role',
                    'is_system_role': True,
                    'permissions': self._get_default_permissions(role_name)
                }
            )
            default_roles.append(role)
        
        # 1. Create Organizations
        self.stdout.write(self.style.SUCCESS(f'\n[1/5] Creating {count} Organizations...'))
        organizations = []
        org_names = [
            'Tech Studios', 'Creative Labs', 'Digital Arts', 'Animation House', 'Visual Effects Co',
            'Media Productions', 'Film Studios', 'Game Dev Inc', 'VR Innovations', '3D Graphics Ltd',
            'Motion Pictures', 'Cinema Works', 'Studio Alpha', 'Beta Productions', 'Gamma Studios',
            'Delta Media', 'Epsilon Arts', 'Zeta Creative', 'Eta Designs', 'Theta Visuals'
        ]
        
        for i in range(count):
            org_name = org_names[i] if i < len(org_names) else f'Organization {i+1}'
            org, created = Organization.objects.get_or_create(
                name=org_name,
                defaults={'slug': org_name.lower().replace(' ', '-')}
            )
            organizations.append(org)
            if created:
                self.stdout.write(f'  [OK] Created: {org_name}')
        
        # 2. Create Teams
        self.stdout.write(self.style.SUCCESS(f'\n[2/5] Creating {count} Teams...'))
        teams = []
        team_names = [
            'Development Team', 'Design Team', 'Animation Team', 'VFX Team', 'Rendering Team',
            'Modeling Team', 'Texturing Team', 'Lighting Team', 'Compositing Team', 'Rigging Team',
            'Story Team', 'Concept Art Team', 'Character Team', 'Environment Team', 'Asset Team',
            'Pipeline Team', 'QA Team', 'Marketing Team', 'Support Team', 'Research Team'
        ]
        
        for i in range(count):
            org = organizations[i % len(organizations)]
            team_name = team_names[i] if i < len(team_names) else f'Team {i+1}'
            team, created = Team.objects.get_or_create(
                name=team_name,
                organization=org,
                defaults={'description': f'Team description for {team_name}'}
            )
            teams.append(team)
            if created:
                self.stdout.write(f'  [OK] Created: {team_name} ({org.name})')
        
        # 3. Create Custom Roles
        self.stdout.write(self.style.SUCCESS(f'\n[3/5] Creating {count} Custom Roles...'))
        custom_roles = []
        role_templates = [
            ('Senior Developer', ['admin.stories', 'admin.assets', 'admin.shots']),
            ('Junior Developer', ['stories.view', 'assets.view']),
            ('Lead Designer', ['admin.stories', 'admin.assets', 'stories.edit']),
            ('UI/UX Designer', ['stories.view', 'assets.view', 'assets.edit']),
            ('3D Artist', ['stories.view', 'assets.view', 'assets.edit', 'shots.view']),
            ('Animator', ['stories.view', 'shots.view', 'shots.edit']),
            ('VFX Artist', ['stories.view', 'shots.view', 'shots.edit']),
            ('Technical Director', ['admin.settings', 'admin.stories', 'admin.assets']),
            ('Producer', ['admin.stories', 'stories.view', 'stories.edit']),
            ('Coordinator', ['stories.view', 'assets.view', 'shots.view']),
            ('Intern', ['stories.view']),
            ('Freelancer', ['stories.view', 'assets.view']),
            ('Consultant', ['admin.settings', 'stories.view']),
            ('Client', ['stories.view']),
            ('Reviewer', ['stories.view', 'stories.edit']),
            ('Editor', ['stories.view', 'stories.edit', 'assets.edit']),
            ('Supervisor', ['admin.stories', 'stories.view', 'stories.edit']),
            ('Manager', ['admin.teams', 'stories.view', 'stories.edit']),
            ('Director', ['admin.settings', 'admin.stories', 'admin.teams']),
            ('Executive', ['admin.settings', 'admin.stories', 'admin.teams', 'admin.users']),
        ]
        
        for i in range(count):
            role_name, permissions = role_templates[i] if i < len(role_templates) else (f'Custom Role {i+1}', ['stories.view'])
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={
                    'description': f'Custom role: {role_name}',
                    'is_system_role': False,
                    'permissions': permissions
                }
            )
            custom_roles.append(role)
            if created:
                self.stdout.write(f'  [OK] Created: {role_name}')
        
        # 4. Create Users
        self.stdout.write(self.style.SUCCESS(f'\n[4/5] Creating {count} Users...'))
        users = []
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Jessica', 'Robert', 'Amanda',
            'William', 'Ashley', 'Richard', 'Melissa', 'Joseph', 'Nicole', 'Thomas', 'Michelle', 'Charles', 'Kimberly'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
            'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee'
        ]
        
        for i in range(count):
            first_name = first_names[i] if i < len(first_names) else f'User{i+1}'
            last_name = last_names[i] if i < len(last_names) else 'Test'
            username = f'{first_name.lower()}.{last_name.lower()}'
            email = f'{username}@example.com'
            
            # Skip if user already exists
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                self.stdout.write(f'  [SKIP] User already exists: {email}')
            else:
                org = organizations[i % len(organizations)]
                team = teams[i % len(teams)]
                role = custom_roles[i % len(custom_roles)]
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='test123',
                    first_name=first_name,
                    last_name=last_name,
                    organization=org,
                    team=team,
                    role=role,
                    bio=f'Bio for {first_name} {last_name}',
                    phone=f'+1-555-{1000+i:04d}',
                    is_active=True
                )
                self.stdout.write(f'  [OK] Created: {email} ({org.name} - {team.name})')
            
            users.append(user)
        
        # 5. Create Invitations
        self.stdout.write(self.style.SUCCESS(f'\n[5/5] Creating {count} Invitations...'))
        invitation_emails = [
            'invite1@example.com', 'invite2@example.com', 'invite3@example.com', 'invite4@example.com',
            'invite5@example.com', 'invite6@example.com', 'invite7@example.com', 'invite8@example.com',
            'invite9@example.com', 'invite10@example.com', 'invite11@example.com', 'invite12@example.com',
            'invite13@example.com', 'invite14@example.com', 'invite15@example.com', 'invite16@example.com',
            'invite17@example.com', 'invite18@example.com', 'invite19@example.com', 'invite20@example.com'
        ]
        
        statuses = ['pending', 'pending', 'pending', 'accepted', 'expired', 'cancelled']
        
        for i in range(count):
            email = invitation_emails[i] if i < len(invitation_emails) else f'invite{i+1}@example.com'
            org = organizations[i % len(organizations)]
            team = teams[i % len(teams)]
            role = custom_roles[i % len(custom_roles)]
            inviter = admin_user if i % 3 == 0 else users[i % len(users)]
            status = statuses[i % len(statuses)]
            
            expires_at = timezone.now() + timedelta(days=7)
            if status == 'expired':
                expires_at = timezone.now() - timedelta(days=1)
            
            accepted_at = None
            if status == 'accepted':
                accepted_at = timezone.now() - timedelta(days=2)
            
            invitation, created = Invitation.objects.get_or_create(
                email=email,
                organization=org,
                team=team,
                defaults={
                    'role': role,
                    'invited_by': inviter,
                    'status': status,
                    'expires_at': expires_at,
                    'accepted_at': accepted_at,
                    'token': secrets.token_urlsafe(32)
                }
            )
            
            if created:
                self.stdout.write(f'  [OK] Created: {email} ({status}) - {org.name} / {team.name}')
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(f'  Organizations: {Organization.objects.count()}')
        self.stdout.write(f'  Teams: {Team.objects.count()}')
        self.stdout.write(f'  Roles: {Role.objects.count()}')
        self.stdout.write(f'  Users: {User.objects.count()}')
        self.stdout.write(f'  Invitations: {Invitation.objects.count()}')
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Dummy data created successfully!\n'))
        self.stdout.write(self.style.WARNING(f'[INFO] Default password for all users: test123'))
        self.stdout.write(self.style.WARNING(f'[INFO] Admin credentials: admin@oneworld3d.com / admin123\n'))

    def _get_default_permissions(self, role_name):
        """Get default permissions for system roles"""
        permissions_map = {
            'Super Admin': ['admin.*'],
            'Admin': ['admin.settings', 'admin.users', 'admin.teams', 'admin.stories'],
            'Project Manager': ['admin.stories', 'stories.view', 'stories.edit'],
            'Artist/Contractor': ['stories.view', 'assets.view', 'assets.edit', 'shots.view', 'shots.edit'],
            'Reviewer': ['stories.view', 'stories.edit'],
            'Viewer': ['stories.view', 'assets.view', 'shots.view'],
        }
        return permissions_map.get(role_name, ['stories.view'])

