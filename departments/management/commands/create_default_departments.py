"""
Management command to create default departments
"""
from django.core.management.base import BaseCommand
from departments.models import Department


class Command(BaseCommand):
    help = 'Create default departments with icons and colors'

    def handle(self, *args, **options):
        # Define default departments with icons and colors
        default_departments = [
            {
                'name': 'Concept Art',
                'department_type': 'concept_art',
                'description': 'Initial visual designs and concepts',
                'icon': '🎨',
                'color': '#E91E63',
                'display_order': 1,
            },
            {
                'name': 'Modeling',
                'department_type': 'modeling',
                'description': '3D model creation',
                'icon': '🏗️',
                'color': '#2196F3',
                'display_order': 2,
            },
            {
                'name': 'Texturing',
                'department_type': 'texturing',
                'description': 'Surface materials and textures',
                'icon': '🎨',
                'color': '#FF9800',
                'display_order': 3,
            },
            {
                'name': 'Rigging',
                'department_type': 'rigging',
                'description': 'Character/object rigging for animation',
                'icon': '🎭',
                'color': '#9C27B0',
                'display_order': 4,
            },
            {
                'name': 'Animation',
                'department_type': 'animation',
                'description': 'Character and object animation',
                'icon': '🎬',
                'color': '#00BCD4',
                'display_order': 5,
            },
            {
                'name': 'Programming/Technology',
                'department_type': 'programming',
                'description': 'Technical implementation, tools, pipelines',
                'icon': '💻',
                'color': '#607D8B',
                'display_order': 6,
            },
            {
                'name': 'Effects',
                'department_type': 'effects',
                'description': 'Visual effects, particle systems, simulations',
                'icon': '✨',
                'color': '#FFC107',
                'display_order': 7,
            },
            {
                'name': 'Lighting and Rendering',
                'department_type': 'lighting_rendering',
                'description': 'Scene lighting and final rendering',
                'icon': '💡',
                'color': '#FFEB3B',
                'display_order': 8,
            },
            {
                'name': 'Farm',
                'department_type': 'farm',
                'description': 'Render farm management and queue',
                'icon': '🖥️',
                'color': '#795548',
                'display_order': 9,
            },
            {
                'name': 'Previs (Pre-visualization)',
                'department_type': 'previs',
                'description': '3D pre-visualization, animatics, rough animation',
                'icon': '🎥',
                'color': '#E91E63',
                'display_order': 10,
            },
            {
                'name': 'Story/Script',
                'department_type': 'story_script',
                'description': 'Story development and script writing',
                'icon': '📝',
                'color': '#3F51B5',
                'display_order': 11,
            },
            {
                'name': 'Pre-Production',
                'department_type': 'pre_production',
                'description': 'Planning, storyboards, reference gathering',
                'icon': '📋',
                'color': '#009688',
                'display_order': 12,
            },
            {
                'name': 'Post-Production',
                'department_type': 'post_production',
                'description': 'Compositing, editing, final assembly',
                'icon': '🎞️',
                'color': '#9E9E9E',
                'display_order': 13,
            },
            {
                'name': 'Audio/Sound',
                'department_type': 'audio_sound',
                'description': 'Sound design, music, voiceover',
                'icon': '🔊',
                'color': '#FF5722',
                'display_order': 14,
            },
            {
                'name': 'Quality Assurance',
                'department_type': 'qa',
                'description': 'Testing, bug tracking, quality control',
                'icon': '✅',
                'color': '#4CAF50',
                'display_order': 15,
            },
            {
                'name': 'Project Management',
                'department_type': 'project_management',
                'description': 'Overall project coordination',
                'icon': '📊',
                'color': '#1976D2',
                'display_order': 16,
            },
            {
                'name': 'Art Direction',
                'department_type': 'art_direction',
                'description': 'Visual style oversight',
                'icon': '🎯',
                'color': '#E91E63',
                'display_order': 17,
            },
            {
                'name': 'Environment Design',
                'department_type': 'environment_design',
                'description': 'Environment and set design',
                'icon': '🌍',
                'color': '#4CAF50',
                'display_order': 18,
            },
            {
                'name': 'Character Design',
                'department_type': 'character_design',
                'description': 'Character concept and design',
                'icon': '👤',
                'color': '#FF9800',
                'display_order': 19,
            },
            {
                'name': 'Asset Management',
                'department_type': 'asset_management',
                'description': 'Asset organization and version control',
                'icon': '📦',
                'color': '#607D8B',
                'display_order': 20,
            },
            {
                'name': 'Layout',
                'department_type': 'layout',
                'description': 'Scene layout and camera placement',
                'icon': '📐',
                'color': '#00BCD4',
                'display_order': 21,
            },
            {
                'name': 'Compositing',
                'department_type': 'compositing',
                'description': 'Final compositing and integration',
                'icon': '🎨',
                'color': '#9C27B0',
                'display_order': 22,
            },
            {
                'name': 'Review/Approval',
                'department_type': 'review_approval',
                'description': 'Review cycles and approvals',
                'icon': '👁️',
                'color': '#F44336',
                'display_order': 23,
            },
        ]

        created_count = 0
        updated_count = 0

        for dept_data in default_departments:
            department, created = Department.objects.get_or_create(
                department_type=dept_data['department_type'],
                defaults={
                    'name': dept_data['name'],
                    'description': dept_data['description'],
                    'icon': dept_data['icon'],
                    'color': dept_data['color'],
                    'display_order': dept_data['display_order'],
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created department: {department.name}')
                )
            else:
                # Update existing department
                department.name = dept_data['name']
                department.description = dept_data['description']
                department.icon = dept_data['icon']
                department.color = dept_data['color']
                department.display_order = dept_data['display_order']
                department.is_active = True
                department.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated department: {department.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} departments and updated {updated_count} departments.'
            )
        )

