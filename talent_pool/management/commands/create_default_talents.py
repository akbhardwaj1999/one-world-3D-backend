"""
Django management command to create default talent pool data
Run with: python manage.py create_default_talents
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from talent_pool.models import Talent
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates default talent pool data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating default talents...'))
        
        # Get or create a default admin user for created_by
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        talents_data = [
            # Voice Actors
            {
                'name': 'John Smith',
                'talent_type': 'voice_actor',
                'email': 'john.smith@voice.com',
                'phone': '+1-555-0101',
                'portfolio_url': 'https://portfolio.com/johnsmith',
                'hourly_rate': Decimal('75.00'),
                'daily_rate': Decimal('600.00'),
                'availability_status': 'available',
                'specializations': ['Cartoon', 'Realistic', 'Fantasy'],
                'languages': ['English', 'Spanish'],
                'notes': 'Experienced voice actor with 10+ years in animation',
                'created_by': admin_user
            },
            {
                'name': 'Sarah Johnson',
                'talent_type': 'voice_actor',
                'email': 'sarah.j@voice.com',
                'phone': '+1-555-0102',
                'portfolio_url': 'https://portfolio.com/sarahj',
                'hourly_rate': Decimal('80.00'),
                'daily_rate': Decimal('650.00'),
                'availability_status': 'available',
                'specializations': ['Cartoon', 'Children', 'Narration'],
                'languages': ['English', 'French'],
                'notes': 'Specializes in children\'s animation voices',
                'created_by': admin_user
            },
            {
                'name': 'Michael Chen',
                'talent_type': 'voice_actor',
                'email': 'm.chen@voice.com',
                'phone': '+1-555-0103',
                'hourly_rate': Decimal('70.00'),
                'daily_rate': Decimal('550.00'),
                'availability_status': 'busy',
                'specializations': ['Realistic', 'Drama', 'Action'],
                'languages': ['English', 'Mandarin'],
                'notes': 'Currently booked for next 2 months',
                'created_by': admin_user
            },
            
            # 3D Artists
            {
                'name': 'Alex Rodriguez',
                'talent_type': '3d_artist',
                'email': 'alex.r@3dartist.com',
                'phone': '+1-555-0201',
                'portfolio_url': 'https://portfolio.com/alexrodriguez',
                'hourly_rate': Decimal('85.00'),
                'daily_rate': Decimal('680.00'),
                'availability_status': 'available',
                'specializations': ['Character Modeling', 'Environment Design'],
                'languages': ['English', 'Spanish'],
                'notes': 'Expert in character and environment modeling',
                'created_by': admin_user
            },
            {
                'name': 'Emma Wilson',
                'talent_type': '3d_artist',
                'email': 'emma.w@3dartist.com',
                'phone': '+1-555-0202',
                'portfolio_url': 'https://portfolio.com/emmawilson',
                'hourly_rate': Decimal('90.00'),
                'daily_rate': Decimal('720.00'),
                'availability_status': 'available',
                'specializations': ['Fantasy', 'Sci-Fi', 'Realistic'],
                'languages': ['English'],
                'notes': 'Specializes in fantasy and sci-fi 3D art',
                'created_by': admin_user
            },
            
            # 3D Modelers
            {
                'name': 'David Kim',
                'talent_type': 'modeler',
                'email': 'david.k@modeler.com',
                'phone': '+1-555-0301',
                'portfolio_url': 'https://portfolio.com/davidkim',
                'hourly_rate': Decimal('75.00'),
                'daily_rate': Decimal('600.00'),
                'availability_status': 'available',
                'specializations': ['Hard Surface', 'Organic', 'Props'],
                'languages': ['English', 'Korean'],
                'notes': 'Expert in hard surface and organic modeling',
                'created_by': admin_user
            },
            {
                'name': 'Lisa Anderson',
                'talent_type': 'modeler',
                'email': 'lisa.a@modeler.com',
                'phone': '+1-555-0302',
                'hourly_rate': Decimal('80.00'),
                'daily_rate': Decimal('640.00'),
                'availability_status': 'available',
                'specializations': ['Character Modeling', 'Creature Design'],
                'languages': ['English'],
                'notes': 'Specializes in character and creature modeling',
                'created_by': admin_user
            },
            
            # Animators
            {
                'name': 'James Brown',
                'talent_type': 'animator',
                'email': 'james.b@animator.com',
                'phone': '+1-555-0401',
                'portfolio_url': 'https://portfolio.com/jamesbrown',
                'hourly_rate': Decimal('95.00'),
                'daily_rate': Decimal('760.00'),
                'availability_status': 'available',
                'specializations': ['Character Animation', 'Facial Animation'],
                'languages': ['English'],
                'notes': 'Expert in character and facial animation',
                'created_by': admin_user
            },
            {
                'name': 'Maria Garcia',
                'talent_type': 'animator',
                'email': 'maria.g@animator.com',
                'phone': '+1-555-0402',
                'hourly_rate': Decimal('100.00'),
                'daily_rate': Decimal('800.00'),
                'availability_status': 'available',
                'specializations': ['Action Animation', 'Comedy', 'Drama'],
                'languages': ['English', 'Spanish'],
                'notes': 'Versatile animator with strong action and comedy skills',
                'created_by': admin_user
            },
            {
                'name': 'Robert Taylor',
                'talent_type': 'animator',
                'email': 'robert.t@animator.com',
                'phone': '+1-555-0403',
                'hourly_rate': Decimal('90.00'),
                'daily_rate': Decimal('720.00'),
                'availability_status': 'busy',
                'specializations': ['Motion Graphics', 'Character Animation'],
                'languages': ['English'],
                'notes': 'Currently working on a major project',
                'created_by': admin_user
            },
            
            # Riggers
            {
                'name': 'Chris Lee',
                'talent_type': 'rigger',
                'email': 'chris.l@rigger.com',
                'phone': '+1-555-0501',
                'portfolio_url': 'https://portfolio.com/chrislee',
                'hourly_rate': Decimal('85.00'),
                'daily_rate': Decimal('680.00'),
                'availability_status': 'available',
                'specializations': ['Character Rigging', 'Facial Rigging'],
                'languages': ['English', 'Chinese'],
                'notes': 'Expert in character and facial rigging systems',
                'created_by': admin_user
            },
            {
                'name': 'Jennifer White',
                'talent_type': 'rigger',
                'email': 'jennifer.w@rigger.com',
                'phone': '+1-555-0502',
                'hourly_rate': Decimal('88.00'),
                'daily_rate': Decimal('704.00'),
                'availability_status': 'available',
                'specializations': ['Creature Rigging', 'Vehicle Rigging'],
                'languages': ['English'],
                'notes': 'Specializes in creature and vehicle rigging',
                'created_by': admin_user
            },
            
            # Texture Artists
            {
                'name': 'Kevin Martinez',
                'talent_type': 'texture_artist',
                'email': 'kevin.m@texture.com',
                'phone': '+1-555-0601',
                'portfolio_url': 'https://portfolio.com/kevinmartinez',
                'hourly_rate': Decimal('75.00'),
                'daily_rate': Decimal('600.00'),
                'availability_status': 'available',
                'specializations': ['PBR Texturing', 'Stylized Textures'],
                'languages': ['English', 'Spanish'],
                'notes': 'Expert in PBR and stylized texture creation',
                'created_by': admin_user
            },
            {
                'name': 'Amanda Davis',
                'talent_type': 'texture_artist',
                'email': 'amanda.d@texture.com',
                'phone': '+1-555-0602',
                'hourly_rate': Decimal('78.00'),
                'daily_rate': Decimal('624.00'),
                'availability_status': 'available',
                'specializations': ['Character Texturing', 'Environment Texturing'],
                'languages': ['English'],
                'notes': 'Specializes in character and environment texturing',
                'created_by': admin_user
            },
            
            # Lighting Artists
            {
                'name': 'Daniel Thompson',
                'talent_type': 'lighting_artist',
                'email': 'daniel.t@lighting.com',
                'phone': '+1-555-0701',
                'portfolio_url': 'https://portfolio.com/danielthompson',
                'hourly_rate': Decimal('92.00'),
                'daily_rate': Decimal('736.00'),
                'availability_status': 'available',
                'specializations': ['Cinematic Lighting', 'Mood Lighting'],
                'languages': ['English'],
                'notes': 'Expert in cinematic and mood lighting',
                'created_by': admin_user
            },
            {
                'name': 'Rachel Green',
                'talent_type': 'lighting_artist',
                'email': 'rachel.g@lighting.com',
                'phone': '+1-555-0702',
                'hourly_rate': Decimal('88.00'),
                'daily_rate': Decimal('704.00'),
                'availability_status': 'available',
                'specializations': ['Realistic Lighting', 'Stylized Lighting'],
                'languages': ['English'],
                'notes': 'Versatile lighting artist for various styles',
                'created_by': admin_user
            },
            
            # Compositors
            {
                'name': 'Thomas Wright',
                'talent_type': 'compositor',
                'email': 'thomas.w@compositor.com',
                'phone': '+1-555-0801',
                'portfolio_url': 'https://portfolio.com/thomaswright',
                'hourly_rate': Decimal('95.00'),
                'daily_rate': Decimal('760.00'),
                'availability_status': 'available',
                'specializations': ['Nuke', 'After Effects', 'Fusion'],
                'languages': ['English'],
                'notes': 'Expert compositor with Nuke and After Effects',
                'created_by': admin_user
            },
            {
                'name': 'Olivia Harris',
                'talent_type': 'compositor',
                'email': 'olivia.h@compositor.com',
                'phone': '+1-555-0802',
                'hourly_rate': Decimal('90.00'),
                'daily_rate': Decimal('720.00'),
                'availability_status': 'available',
                'specializations': ['VFX Compositing', 'Color Grading'],
                'languages': ['English', 'French'],
                'notes': 'Specializes in VFX compositing and color grading',
                'created_by': admin_user
            },
            
            # Other
            {
                'name': 'Steven Moore',
                'talent_type': 'other',
                'email': 'steven.m@freelance.com',
                'phone': '+1-555-0901',
                'portfolio_url': 'https://portfolio.com/stevenmoore',
                'hourly_rate': Decimal('70.00'),
                'daily_rate': Decimal('560.00'),
                'availability_status': 'available',
                'specializations': ['Generalist', 'Pipeline', 'Technical Art'],
                'languages': ['English'],
                'notes': 'Generalist with pipeline and technical art skills',
                'created_by': admin_user
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for talent_data in talents_data:
            talent, created = Talent.objects.get_or_create(
                email=talent_data['email'],
                defaults=talent_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[+] Created talent: {talent.name} ({talent.get_talent_type_display()})')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'[-] Skipped (already exists): {talent.name}')
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully created {created_count} talents'
        ))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(
                f'Skipped {skipped_count} talents (already exist)'
            ))
        
        total_talents = Talent.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'\nTotal talents in database: {total_talents}'
        ))

