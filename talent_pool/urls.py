from django.urls import path
from .views import (
    talent_list_create,
    talent_detail,
    character_talent_assignments,
    character_talent_assignment_detail,
    asset_talent_assignments,
    asset_talent_assignment_detail,
    shot_talent_assignments,
    shot_talent_assignment_detail,
)

app_name = 'talent_pool'

urlpatterns = [
    # Talent CRUD endpoints
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

