from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization, Team, Role, StoryAccess, Invitation


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'created_at']
    list_filter = ['organization', 'created_at']
    search_fields = ['name', 'organization__name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_system_role', 'created_at']
    list_filter = ['is_system_role', 'created_at']
    search_fields = ['name', 'description']


@admin.register(StoryAccess)
class StoryAccessAdmin(admin.ModelAdmin):
    list_display = ['story', 'user', 'team', 'can_view', 'can_edit', 'can_delete']
    list_filter = ['can_view', 'can_edit', 'can_delete']
    search_fields = ['story__title', 'user__email', 'team__name']


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'organization', 'team', 'role', 'status', 'created_at', 'expires_at']
    list_filter = ['status', 'created_at', 'expires_at']
    search_fields = ['email', 'organization__name', 'team__name']
    readonly_fields = ['token', 'created_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'organization', 'team', 'role', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'organization', 'team', 'role', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio', 'phone')}),
        ('Organization', {'fields': ('organization', 'team', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
