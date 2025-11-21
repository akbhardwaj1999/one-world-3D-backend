from django.urls import path
from .views import (
    parse_story,
    story_list,
    story_detail,
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

app_name = 'ai_machines'

urlpatterns = [
    path('parse-story/', parse_story, name='parse_story'),
    path('stories/', story_list, name='story_list'),
    path('stories/<int:story_id>/', story_detail, name='story_detail'),
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
]
