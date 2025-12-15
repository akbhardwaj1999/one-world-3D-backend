"""
Management command to create default roles with permissions
"""
from django.core.management.base import BaseCommand
from accounts.models import Role


class Command(BaseCommand):
    help = 'Create default roles with permissions'

    def handle(self, *args, **options):
        # Define default roles with their permissions
        default_roles = [
            {
                'name': 'Super Admin',
                'description': 'Full system access with all permissions',
                'is_system_role': True,
                'permissions': [
                    # Admin permissions
                    'admin.users', 'admin.teams', 'admin.roles', 'admin.settings',
                    # Story permissions
                    'stories.view', 'stories.create', 'stories.edit', 'stories.delete', 'stories.duplicate', 'stories.export',
                    # Asset permissions
                    'assets.view', 'assets.create', 'assets.edit', 'assets.delete', 'assets.assign', 'assets.approve',
                    # Shot permissions
                    'shots.view', 'shots.create', 'shots.edit', 'shots.delete', 'shots.assign', 'shots.approve',
                    # Department permissions
                    'departments.view', 'departments.assign', 'departments.manage',
                    # Talent permissions
                    'talent.view', 'talent.assign', 'talent.manage',
                    # Cost permissions
                    'costs.view', 'costs.edit', 'costs.export',
                    # Generation permissions
                    'generation.create', 'generation.view', 'generation.delete',
                    # Art control permissions
                    'art_control.view', 'art_control.edit',
                ]
            },
            {
                'name': 'Admin',
                'description': 'Team administrator with management permissions',
                'is_system_role': True,
                'permissions': [
                    'admin.users', 'admin.teams',
                    'stories.view', 'stories.create', 'stories.edit', 'stories.delete', 'stories.duplicate', 'stories.export',
                    'assets.view', 'assets.create', 'assets.edit', 'assets.delete', 'assets.assign', 'assets.approve',
                    'shots.view', 'shots.create', 'shots.edit', 'shots.delete', 'shots.assign', 'shots.approve',
                    'departments.view', 'departments.assign', 'departments.manage',
                    'talent.view', 'talent.assign', 'talent.manage',
                    'costs.view', 'costs.edit', 'costs.export',
                    'generation.create', 'generation.view', 'generation.delete',
                    'art_control.view', 'art_control.edit',
                ]
            },
            {
                'name': 'Project Manager',
                'description': 'Manage projects and assign work',
                'is_system_role': True,
                'permissions': [
                    'stories.view', 'stories.create', 'stories.edit', 'stories.duplicate', 'stories.export',
                    'assets.view', 'assets.create', 'assets.edit', 'assets.assign', 'assets.approve',
                    'shots.view', 'shots.create', 'shots.edit', 'shots.assign', 'shots.approve',
                    'departments.view', 'departments.assign',
                    'talent.view', 'talent.assign',
                    'costs.view', 'costs.export',
                    'generation.create', 'generation.view',
                    'art_control.view', 'art_control.edit',
                ]
            },
            {
                'name': 'Artist/Contractor',
                'description': 'View and work on assigned tasks',
                'is_system_role': True,
                'permissions': [
                    'stories.view',
                    'assets.view',
                    'shots.view',
                    'departments.view',
                    'talent.view',
                    'generation.view',
                ]
            },
            {
                'name': 'Reviewer',
                'description': 'Review and approve work',
                'is_system_role': True,
                'permissions': [
                    'stories.view',
                    'assets.view', 'assets.approve',
                    'shots.view', 'shots.approve',
                    'departments.view',
                ]
            },
            {
                'name': 'Viewer',
                'description': 'Read-only access to stories',
                'is_system_role': True,
                'permissions': [
                    'stories.view',
                    'assets.view',
                    'shots.view',
                    'departments.view',
                ]
            },
        ]

        created_count = 0
        updated_count = 0

        for role_data in default_roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'is_system_role': role_data['is_system_role'],
                    'permissions': role_data['permissions'],
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.name}')
                )
            else:
                # Update existing role
                role.description = role_data['description']
                role.is_system_role = role_data['is_system_role']
                role.permissions = role_data['permissions']
                role.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated role: {role.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} roles and updated {updated_count} roles.'
            )
        )

