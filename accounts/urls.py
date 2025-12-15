from django.urls import path
from . import views
from . import user_management_views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # User Management
    path('users/', user_management_views.user_list, name='user_list'),
    path('users/<int:pk>/', user_management_views.user_detail, name='user_detail'),
    path('users/<int:pk>/update/', user_management_views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', user_management_views.user_delete, name='user_delete'),
    
    # Organizations
    path('organizations/', user_management_views.organization_list_create, name='organization_list_create'),
    path('organizations/<int:pk>/', user_management_views.organization_detail, name='organization_detail'),
    
    # Teams
    path('teams/', user_management_views.team_list_create, name='team_list_create'),
    path('teams/<int:pk>/', user_management_views.team_detail, name='team_detail'),
    path('teams/<int:pk>/members/', user_management_views.team_members, name='team_members'),
    path('teams/<int:pk>/members/<int:user_id>/remove/', user_management_views.team_member_remove, name='team_member_remove'),
    
    # Roles
    path('roles/', user_management_views.role_list_create, name='role_list_create'),
    path('roles/<int:pk>/', user_management_views.role_detail, name='role_detail'),
    
    # Invitations
    path('invitations/', user_management_views.invitation_list_create, name='invitation_list_create'),
    path('invitations/<str:token>/', user_management_views.invitation_detail, name='invitation_detail'),
    path('invitations/<str:token>/accept/', user_management_views.invitation_accept, name='invitation_accept'),
    path('invitations/<int:pk>/cancel/', user_management_views.invitation_cancel, name='invitation_cancel'),
    
    # Story Access
    path('stories/<int:story_id>/access/', user_management_views.story_access_list_create, name='story_access_list_create'),
    path('stories/<int:story_id>/access/<int:access_id>/', user_management_views.story_access_detail, name='story_access_detail'),
]

