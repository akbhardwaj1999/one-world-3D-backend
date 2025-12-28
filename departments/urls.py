from django.urls import path
from .views import (
    department_list_create,
    department_detail,
    story_departments,
    story_department_remove,
    asset_department_assignments,
    asset_department_assignment_detail,
    shot_department_assignments,
    shot_department_assignment_detail,
    department_stats,
    department_assets,
    department_shots,
)

app_name = 'departments'

urlpatterns = [
    # Department CRUD
    path('', department_list_create, name='department_list_create'),
    path('<int:department_id>/', department_detail, name='department_detail'),
    # Story Departments
    path('stories/<int:story_id>/', story_departments, name='story_departments'),
    path('stories/<int:story_id>/<int:department_id>/', story_department_remove, name='story_department_remove'),
    path('stories/<int:story_id>/<int:department_id>/stats/', department_stats, name='department_stats'),
    path('stories/<int:story_id>/<int:department_id>/assets/', department_assets, name='department_assets'),
    path('stories/<int:story_id>/<int:department_id>/shots/', department_shots, name='department_shots'),
    # Asset Department Assignments
    path('stories/<int:story_id>/assets/<int:asset_id>/', asset_department_assignments, name='asset_department_assignments'),
    path('assignments/asset/<int:assignment_id>/', asset_department_assignment_detail, name='asset_department_assignment_detail'),
    # Shot Department Assignments
    path('stories/<int:story_id>/shots/<int:shot_id>/', shot_department_assignments, name='shot_department_assignments'),
    path('assignments/shot/<int:assignment_id>/', shot_department_assignment_detail, name='shot_department_assignment_detail'),
]

