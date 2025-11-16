from django.urls import path
from .views import (
    parse_story,
    art_control_settings,
    reset_art_control_settings,
    sequence_art_control_settings,
    shot_art_control_settings,
)

app_name = 'ai_machines'

urlpatterns = [
    path('parse-story/', parse_story, name='parse_story'),
    path('stories/<int:story_id>/art-control/', art_control_settings, name='art_control_settings'),
    path('stories/<int:story_id>/art-control/reset/', reset_art_control_settings, name='reset_art_control_settings'),
    path('stories/<int:story_id>/sequences/<int:sequence_id>/art-control/', sequence_art_control_settings, name='sequence_art_control_settings'),
    path('stories/<int:story_id>/shots/<int:shot_id>/art-control/', shot_art_control_settings, name='shot_art_control_settings'),
]
