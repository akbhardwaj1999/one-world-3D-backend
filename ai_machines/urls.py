from django.urls import path
from .views import (
    parse_story,
    story_list,
    story_detail,
    story_cost_breakdown,
    art_control_settings,
    reset_art_control_settings,
    sequence_art_control_settings,
    shot_art_control_settings,
)
from .chat_views import (
    chat_list,
    chat_create,
    chat_detail,
    chat_update,
    chat_delete,
)
from .talent_views import (
    talent_list_create,
    talent_detail,
    character_talent_assignments,
    character_talent_assignment_detail,
    asset_talent_assignments,
    asset_talent_assignment_detail,
    shot_talent_assignments,
    shot_talent_assignment_detail,
)

app_name = 'ai_machines'

urlpatterns = [
    path('parse-story/', parse_story, name='parse_story'),
    path('stories/', story_list, name='story_list'),
    path('stories/<int:story_id>/', story_detail, name='story_detail'),
    path('stories/<int:story_id>/cost-breakdown/', story_cost_breakdown, name='story_cost_breakdown'),
    path('stories/<int:story_id>/art-control/', art_control_settings, name='art_control_settings'),
    path('stories/<int:story_id>/art-control/reset/', reset_art_control_settings, name='reset_art_control_settings'),
    path('stories/<int:story_id>/sequences/<int:sequence_id>/art-control/', sequence_art_control_settings, name='sequence_art_control_settings'),
    path('stories/<int:story_id>/shots/<int:shot_id>/art-control/', shot_art_control_settings, name='shot_art_control_settings'),
    # Chat endpoints
    path('chats/', chat_list, name='chat_list'),
    path('chats/create/', chat_create, name='chat_create'),
    path('chats/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('chats/<int:chat_id>/update/', chat_update, name='chat_update'),
    path('chats/<int:chat_id>/delete/', chat_delete, name='chat_delete'),
    # Talent Pool endpoints
    path('talent/', talent_list_create, name='talent_list_create'),
    path('talent/<int:talent_id>/', talent_detail, name='talent_detail'),
    # Character Talent Assignments
    path('stories/<int:story_id>/characters/<int:character_id>/talent/', character_talent_assignments, name='character_talent_assignments'),
    path('talent-assignments/character/<int:assignment_id>/', character_talent_assignment_detail, name='character_talent_assignment_detail'),
    # Asset Talent Assignments
    path('stories/<int:story_id>/assets/<int:asset_id>/talent/', asset_talent_assignments, name='asset_talent_assignments'),
    path('talent-assignments/asset/<int:assignment_id>/', asset_talent_assignment_detail, name='asset_talent_assignment_detail'),
    # Shot Talent Assignments
    path('stories/<int:story_id>/shots/<int:shot_id>/talent/', shot_talent_assignments, name='shot_talent_assignments'),
    path('talent-assignments/shot/<int:assignment_id>/', shot_talent_assignment_detail, name='shot_talent_assignment_detail'),
]
