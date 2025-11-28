from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Story(models.Model):
    """Story Model - Stores parsed stories"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=255)
    raw_text = models.TextField()
    parsed_data = models.JSONField(default=dict)  # Full parsed JSON
    summary = models.TextField(blank=True)
    total_shots = models.IntegerField(default=0)
    estimated_total_time = models.CharField(max_length=100, blank=True)
    total_estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_range = models.CharField(max_length=50, blank=True)  # e.g., "$50k-$100k"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Character(models.Model):
    """Character extracted from story"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    role = models.CharField(max_length=100, blank=True)  # protagonist, antagonist, supporting
    appearances = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'story_characters'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.story.title})"


class Location(models.Model):
    """Location extracted from story"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location_type = models.CharField(max_length=100, blank=True)  # indoor, outdoor, fantasy, etc.
    scenes = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'story_locations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.story.title})"


class StoryAsset(models.Model):
    """Asset extracted from story"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_assets')
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=50)  # model, prop, environment, effect
    description = models.TextField(blank=True)
    complexity = models.CharField(max_length=20, default='medium')  # low, medium, high
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=100.00)
    
    class Meta:
        db_table = 'story_assets'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.story.title})"


class Sequence(models.Model):
    """Sequence extracted from story - A sequence contains multiple shots"""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='sequences')
    sequence_number = models.IntegerField()
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='sequences')
    characters = models.ManyToManyField(Character, related_name='sequences', blank=True)
    estimated_time = models.CharField(max_length=100, blank=True)
    total_shots = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'story_sequences'
        ordering = ['sequence_number']
    
    def __str__(self):
        return f"Sequence {self.sequence_number} - {self.story.title}"


class Shot(models.Model):
    """Shot extracted from story - Individual camera shots within a sequence"""
    COMPLEXITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='shots')
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name='shots', null=True, blank=True)
    shot_number = models.IntegerField()
    description = models.TextField()
    characters = models.ManyToManyField(Character, related_name='shots', blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='shots')
    camera_angle = models.CharField(max_length=100, blank=True)
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, default='medium')
    estimated_time = models.CharField(max_length=100, blank=True)
    special_requirements = models.JSONField(default=list, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'story_shots'
        ordering = ['shot_number']
    
    def __str__(self):
        return f"Shot {self.shot_number} - {self.story.title}"


class ArtControlSettings(models.Model):
    """Art control settings for a story, sequence, or shot"""
    # Can be attached to story, sequence, or shot (exactly one must be set)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='art_control', null=True, blank=True)
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name='art_control', null=True, blank=True)
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE, related_name='art_control', null=True, blank=True)
    
    # Color Palette
    primary_colors = models.JSONField(default=list)  # [{"name": "Hero Blue", "hex": "#1E88E5", "usage": "primary"}]
    color_mood = models.CharField(
        max_length=50,
        choices=[
            ('warm', 'Warm'),
            ('cool', 'Cool'),
            ('neutral', 'Neutral'),
        ],
        default='neutral'
    )
    color_saturation = models.CharField(
        max_length=50,
        choices=[
            ('high', 'High Saturation'),
            ('medium', 'Medium Saturation'),
            ('low', 'Low Saturation'),
            ('desaturated', 'Desaturated'),
        ],
        default='medium'
    )
    color_contrast = models.CharField(
        max_length=50,
        choices=[
            ('high', 'High Contrast'),
            ('medium', 'Medium Contrast'),
            ('low', 'Low Contrast'),
        ],
        default='medium'
    )
    forbidden_colors = models.JSONField(default=list)  # Hex codes to avoid
    
    # Composition
    composition_style = models.CharField(
        max_length=50,
        choices=[
            ('rule_of_thirds', 'Rule of Thirds'),
            ('symmetrical', 'Symmetrical'),
            ('asymmetrical', 'Asymmetrical'),
            ('centered', 'Centered'),
            ('dynamic', 'Dynamic'),
        ],
        default='rule_of_thirds'
    )
    preferred_shot_types = models.JSONField(default=list)  # ['wide', 'medium', 'close-up']
    
    # Camera Guidelines
    handheld_allowed = models.BooleanField(default=False)
    stable_camera_allowed = models.BooleanField(default=True)
    gimbal_allowed = models.BooleanField(default=True)
    drone_allowed = models.BooleanField(default=False)
    static_camera_allowed = models.BooleanField(default=True)
    
    # Lens Guidelines
    wide_angle_allowed = models.BooleanField(default=True)
    standard_lens_preferred = models.BooleanField(default=True)
    telephoto_allowed = models.BooleanField(default=True)
    macro_allowed = models.BooleanField(default=False)
    fisheye_allowed = models.BooleanField(default=False)
    
    # Camera Movement
    static_shots_only = models.BooleanField(default=False)
    panning_allowed = models.BooleanField(default=True)
    tracking_allowed = models.BooleanField(default=True)
    zoom_allowed = models.BooleanField(default=True)
    dolly_shots_allowed = models.BooleanField(default=True)
    
    # Visual Style
    art_style = models.CharField(
        max_length=50,
        choices=[
            ('realistic', 'Realistic'),
            ('stylized', 'Stylized'),
            ('cartoon', 'Cartoon'),
            ('anime', 'Anime'),
            ('watercolor', 'Watercolor'),
            ('oil_painting', 'Oil Painting'),
            ('digital_art', 'Digital Art'),
        ],
        default='realistic'
    )
    detail_level = models.CharField(
        max_length=50,
        choices=[
            ('high', 'High Detail'),
            ('medium', 'Medium Detail'),
            ('low', 'Low Detail'),
        ],
        default='medium'
    )
    lighting_style = models.CharField(
        max_length=50,
        choices=[
            ('natural', 'Natural Lighting'),
            ('dramatic', 'Dramatic Lighting'),
            ('soft', 'Soft Lighting'),
            ('high_key', 'High Key'),
            ('low_key', 'Low Key'),
        ],
        default='natural'
    )
    
    # Animation Style
    animation_type = models.CharField(
        max_length=50,
        choices=[
            ('smooth', 'Smooth/Realistic'),
            ('stylized', 'Stylized/Exaggerated'),
            ('stop_motion', 'Stop-Motion Style'),
            ('2d_style', '2D Animation Style'),
        ],
        default='smooth'
    )
    motion_preference = models.CharField(
        max_length=50,
        choices=[
            ('fast', 'Fast-Paced'),
            ('slow', 'Slow and Deliberate'),
            ('natural', 'Natural Timing'),
            ('exaggerated', 'Exaggerated Timing'),
        ],
        default='natural'
    )
    
    # Reference Images
    style_reference_images = models.JSONField(default=list)  # URLs to reference images
    mood_board_images = models.JSONField(default=list)  # Enhanced mood board with multiple reference images
    
    # Story Level Only - Technical Specifications
    frame_rate = models.CharField(
        max_length=20,
        choices=[
            ('24', '24 fps (Cinematic)'),
            ('30', '30 fps (Standard)'),
            ('60', '60 fps (Smooth)'),
            ('120', '120 fps (High Frame Rate)'),
        ],
        default='24',
        blank=True,
        null=True
    )
    resolution = models.CharField(
        max_length=20,
        choices=[
            ('1080p', '1080p (Full HD)'),
            ('2K', '2K (1440p)'),
            ('4K', '4K (2160p)'),
            ('8K', '8K (4320p)'),
        ],
        default='1080p',
        blank=True,
        null=True
    )
    
    # Aspect Ratio (story level only, but can be set at any level)
    aspect_ratio = models.CharField(
        max_length=20,
        choices=[
            ('16:9', '16:9 (Widescreen)'),
            ('21:9', '21:9 (Ultrawide)'),
            ('4:3', '4:3 (Standard)'),
            ('1:1', '1:1 (Square)'),
            ('9:16', '9:16 (Portrait)'),
            ('custom', 'Custom'),
        ],
        default='16:9',
        blank=True
    )
    custom_aspect_ratio = models.CharField(max_length=20, blank=True)  # e.g., "2.35:1"
    
    # Sequence/Shot Level - Environment & Timing
    atmosphere = models.CharField(
        max_length=50,
        choices=[
            ('foggy', 'Foggy'),
            ('clear', 'Clear'),
            ('dusty', 'Dusty'),
            ('ethereal', 'Ethereal'),
            ('misty', 'Misty'),
            ('hazy', 'Hazy'),
            ('crisp', 'Crisp'),
        ],
        blank=True,
        null=True
    )
    time_of_day = models.CharField(
        max_length=50,
        choices=[
            ('dawn', 'Dawn'),
            ('day', 'Day'),
            ('dusk', 'Dusk'),
            ('night', 'Night'),
            ('golden_hour', 'Golden Hour'),
            ('blue_hour', 'Blue Hour'),
        ],
        blank=True,
        null=True
    )
    shot_duration = models.CharField(
        max_length=50,
        choices=[
            ('fast_paced', 'Fast-Paced (Quick Cuts)'),
            ('standard', 'Standard'),
            ('slow_paced', 'Slow-Paced (Long Takes)'),
        ],
        blank=True,
        null=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'art_control_settings'
        ordering = ['-updated_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(story__isnull=False) & models.Q(sequence__isnull=True) & models.Q(shot__isnull=True)) |
                    (models.Q(story__isnull=True) & models.Q(sequence__isnull=False) & models.Q(shot__isnull=True)) |
                    (models.Q(story__isnull=True) & models.Q(sequence__isnull=True) & models.Q(shot__isnull=False))
                ),
                name='exactly_one_parent'
            )
        ]
    
    def __str__(self):
        if self.story:
            return f"Art Control - Story: {self.story.title}"
        elif self.sequence:
            return f"Art Control - Sequence {self.sequence.sequence_number}"
        elif self.shot:
            return f"Art Control - Shot {self.shot.shot_number}"
        return "Art Control - Unknown"


class Chat(models.Model):
    """Chat Model - Stores user chat conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    title = models.CharField(max_length=255, default='New Chat')
    messages = models.JSONField(default=list)  # List of message objects
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chats'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Talent(models.Model):
    """Talent pool - External contractors (voice actors, artists, etc.)"""
    TALENT_TYPES = [
        ('voice_actor', 'Voice Actor'),
        ('3d_artist', '3D Artist'),
        ('modeler', '3D Modeler'),
        ('animator', 'Animator'),
        ('rigger', 'Rigger'),
        ('texture_artist', 'Texture Artist'),
        ('lighting_artist', 'Lighting Artist'),
        ('compositor', 'Compositor'),
        ('other', 'Other'),
    ]
    
    AVAILABILITY_STATUS = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('unavailable', 'Unavailable'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=255)
    talent_type = models.CharField(max_length=50, choices=TALENT_TYPES)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    portfolio_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    # Rates & Availability
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default='available'
    )
    
    # Skills & Specializations
    specializations = models.JSONField(default=list, blank=True)  # e.g., ["cartoon", "realistic", "fantasy"]
    languages = models.JSONField(default=list, blank=True)  # e.g., ["English", "Spanish"]
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_talent'
    )
    
    class Meta:
        db_table = 'talent_pool'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_talent_type_display()})"


class CharacterTalentAssignment(models.Model):
    """Link voice actors to characters"""
    ROLE_TYPES = [
        ('voice_actor', 'Voice Actor'),
        ('motion_capture', 'Motion Capture'),
        ('reference_model', 'Reference Model'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('contacted', 'Contacted'),
        ('negotiating', 'Negotiating'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ]
    
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='talent_assignments')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='character_assignments')
    role_type = models.CharField(
        max_length=50,
        choices=ROLE_TYPES,
        default='voice_actor'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed'
    )
    rate_agreed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'character_talent_assignments'
        unique_together = ['character', 'talent', 'role_type']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.talent.name} → {self.character.name} ({self.get_role_type_display()})"


class AssetTalentAssignment(models.Model):
    """Link artists to assets"""
    ROLE_TYPES = [
        ('modeler', '3D Modeler'),
        ('texture_artist', 'Texture Artist'),
        ('rigger', 'Rigger'),
        ('concept_artist', 'Concept Artist'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('contacted', 'Contacted'),
        ('negotiating', 'Negotiating'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    asset = models.ForeignKey(StoryAsset, on_delete=models.CASCADE, related_name='talent_assignments')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='asset_assignments')
    role_type = models.CharField(
        max_length=50,
        choices=ROLE_TYPES,
        default='modeler'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed'
    )
    rate_agreed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_hours = models.IntegerField(null=True, blank=True)
    actual_hours = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'asset_talent_assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.talent.name} → {self.asset.name} ({self.get_role_type_display()})"


class ShotTalentAssignment(models.Model):
    """Link animators/specialists to shots"""
    ROLE_TYPES = [
        ('animator', 'Animator'),
        ('lighting_artist', 'Lighting Artist'),
        ('compositor', 'Compositor'),
        ('fx_artist', 'FX Artist'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('contacted', 'Contacted'),
        ('negotiating', 'Negotiating'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE, related_name='talent_assignments')
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE, related_name='shot_assignments')
    role_type = models.CharField(
        max_length=50,
        choices=ROLE_TYPES,
        default='animator'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed'
    )
    rate_agreed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_hours = models.IntegerField(null=True, blank=True)
    actual_hours = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shot_talent_assignments'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.talent.name} → Shot {self.shot.shot_number} ({self.get_role_type_display()})"