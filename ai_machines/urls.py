from django.urls import path
from .views import (
    parse_story,
    story_list,
    story_detail,
    story_cost_breakdown,
    regenerate_story,
    art_control_settings,
    reset_art_control_settings,
    sequence_art_control_settings,
    shot_art_control_settings,
    asset_detail,
    asset_update,
    asset_upload_images,
    asset_delete_image,
    character_detail,
    character_update,
    character_upload_images,
    character_delete_image,
    location_detail,
    location_update,
    location_upload_images,
    location_delete_image,
    sequence_detail,
    sequence_update,
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
    path('stories/<int:story_id>/regenerate/', regenerate_story, name='regenerate_story'),
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
    # Asset endpoints
    path('stories/<int:story_id>/assets/<int:asset_id>/', asset_detail, name='asset_detail'),
    path('stories/<int:story_id>/assets/<int:asset_id>/update/', asset_update, name='asset_update'),
    path('stories/<int:story_id>/assets/<int:asset_id>/upload-images/', asset_upload_images, name='asset_upload_images'),
    path('stories/<int:story_id>/assets/<int:asset_id>/images/<int:image_id>/', asset_delete_image, name='asset_delete_image'),
    # Character endpoints
    path('stories/<int:story_id>/characters/<int:character_id>/', character_detail, name='character_detail'),
    path('stories/<int:story_id>/characters/<int:character_id>/update/', character_update, name='character_update'),
    path('stories/<int:story_id>/characters/<int:character_id>/upload-images/', character_upload_images, name='character_upload_images'),
    path('stories/<int:story_id>/characters/<int:character_id>/images/<int:image_id>/', character_delete_image, name='character_delete_image'),
    # Location endpoints
    path('stories/<int:story_id>/locations/<int:location_id>/', location_detail, name='location_detail'),
    path('stories/<int:story_id>/locations/<int:location_id>/update/', location_update, name='location_update'),
    path('stories/<int:story_id>/locations/<int:location_id>/upload-images/', location_upload_images, name='location_upload_images'),
    path('stories/<int:story_id>/locations/<int:location_id>/images/<int:image_id>/', location_delete_image, name='location_delete_image'),
    # Sequence endpoints
    path('stories/<int:story_id>/sequences/<int:sequence_id>/', sequence_detail, name='sequence_detail'),
    path('stories/<int:story_id>/sequences/<int:sequence_id>/update/', sequence_update, name='sequence_update'),
]
