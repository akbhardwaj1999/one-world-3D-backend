from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Organization, Team, Role, StoryAccess, Invitation


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization Serializer"""
    teams_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'created_at', 'teams_count', 'members_count']
        read_only_fields = ['id', 'slug', 'created_at']
    
    def get_teams_count(self, obj):
        return obj.teams.count()
    
    def get_members_count(self, obj):
        return obj.members.count()


class TeamSerializer(serializers.ModelSerializer):
    """Team Serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'organization', 'organization_name', 'created_at', 'members_count']
        read_only_fields = ['id', 'created_at']
    
    def get_members_count(self, obj):
        return obj.members.count()


class RoleSerializer(serializers.ModelSerializer):
    """Role Serializer"""
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_system_role', 'permissions', 'created_at', 'updated_at', 'users_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_users_count(self, obj):
        return obj.users.count()


class UserSerializer(serializers.ModelSerializer):
    """User Serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'organization', 'organization_name', 'team', 'team_name', 
            'role', 'role_name', 'avatar', 'bio', 'phone', 
            'is_active', 'is_staff', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Don't show password-related fields
        data.pop('password', None)
        return data


class StoryAccessSerializer(serializers.ModelSerializer):
    """Story Access Serializer"""
    story_title = serializers.CharField(source='story.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = StoryAccess
        fields = [
            'id', 'story', 'story_title', 'user', 'user_email', 
            'team', 'team_name', 'can_view', 'can_edit', 'can_delete'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        # Either user or team must be provided, not both
        user = attrs.get('user')
        team = attrs.get('team')
        
        # For updates, if neither is provided, check if instance has one
        if not user and not team:
            if self.instance:
                # Update case - keep existing user/team if not provided
                return attrs
            else:
                # Create case - must provide one
                raise serializers.ValidationError("Either user or team must be provided.")
        
        if user and team:
            raise serializers.ValidationError("Cannot assign both user and team. Choose one.")
        
        return attrs


class InvitationSerializer(serializers.ModelSerializer):
    """Invitation Serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    invited_by_name = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 'organization', 'organization_name', 
            'team', 'team_name', 'role', 'role_name', 
            'token', 'invited_by', 'invited_by_name', 
            'status', 'created_at', 'expires_at', 'accepted_at', 'is_expired'
        ]
        read_only_fields = ['id', 'token', 'invited_by', 'created_at', 'accepted_at', 'expires_at']
    
    def get_invited_by_name(self, obj):
        return f"{obj.invited_by.first_name} {obj.invited_by.last_name}".strip() or obj.invited_by.email
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class RegisterSerializer(serializers.ModelSerializer):
    """Registration Serializer"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Login Serializer"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    """Forgot Password Serializer"""
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Reset Password Serializer"""
    token = serializers.CharField(required=True)
    uid = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

