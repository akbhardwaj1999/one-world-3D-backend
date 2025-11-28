"""
Talent Pool API Views
Handles talent management and assignments
"""
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from .models import (
    Talent, CharacterTalentAssignment, AssetTalentAssignment, ShotTalentAssignment,
    Story, Character, StoryAsset, Shot
)
from .serializers import (
    TalentSerializer, CharacterTalentAssignmentSerializer,
    AssetTalentAssignmentSerializer, ShotTalentAssignmentSerializer
)


# ==================== Talent CRUD ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def talent_list_create(request):
    """
    List all talent or create new talent
    GET /api/ai-machines/talent/
    POST /api/ai-machines/talent/
    """
    if request.method == 'GET':
        try:
            # Get query parameters for filtering
            talent_type = request.query_params.get('talent_type', None)
            availability_status = request.query_params.get('availability_status', None)
            search = request.query_params.get('search', None)
            
            # Start with all talent
            queryset = Talent.objects.all()
            
            # Apply filters
            if talent_type:
                queryset = queryset.filter(talent_type=talent_type)
            if availability_status:
                queryset = queryset.filter(availability_status=availability_status)
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(notes__icontains=search)
                )
            
            # Order by name
            queryset = queryset.order_by('name')
            
            serializer = TalentSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return Response(
                {'error': f'Error fetching talent: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            serializer = TalentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return Response(
                {'error': f'Error creating talent: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def talent_detail(request, talent_id):
    """
    Get, update, or delete a talent
    GET /api/ai-machines/talent/{id}/
    PUT /api/ai-machines/talent/{id}/
    DELETE /api/ai-machines/talent/{id}/
    """
    try:
        talent = get_object_or_404(Talent, id=talent_id)
        
        if request.method == 'GET':
            serializer = TalentSerializer(talent)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            serializer = TalentSerializer(talent, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            talent.delete()
            return Response({'message': 'Talent deleted successfully'}, status=status.HTTP_200_OK)
            
    except Talent.DoesNotExist:
        return Response(
            {'error': 'Talent not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing talent: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Character Talent Assignments ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def character_talent_assignments(request, story_id, character_id):
    """
    Get or create character talent assignments
    GET /api/ai-machines/stories/{story_id}/characters/{character_id}/talent/
    POST /api/ai-machines/stories/{story_id}/characters/{character_id}/talent/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        character = get_object_or_404(Character, id=character_id, story=story)
        
        if request.method == 'GET':
            assignments = CharacterTalentAssignment.objects.filter(character=character)
            serializer = CharacterTalentAssignmentSerializer(assignments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            data = request.data.copy()
            data['character'] = character.id
            serializer = CharacterTalentAssignmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except (Story.DoesNotExist, Character.DoesNotExist):
        return Response(
            {'error': 'Story or Character not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing assignment: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def character_talent_assignment_detail(request, assignment_id):
    """
    Update or delete character talent assignment
    PUT /api/ai-machines/talent-assignments/character/{id}/
    DELETE /api/ai-machines/talent-assignments/character/{id}/
    """
    try:
        assignment = get_object_or_404(CharacterTalentAssignment, id=assignment_id)
        # Verify user owns the story
        if assignment.character.story.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'PUT':
            serializer = CharacterTalentAssignmentSerializer(assignment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            assignment.delete()
            return Response({'message': 'Assignment deleted successfully'}, status=status.HTTP_200_OK)
            
    except CharacterTalentAssignment.DoesNotExist:
        return Response(
            {'error': 'Assignment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing assignment: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Asset Talent Assignments ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def asset_talent_assignments(request, story_id, asset_id):
    """
    Get or create asset talent assignments
    GET /api/ai-machines/stories/{story_id}/assets/{asset_id}/talent/
    POST /api/ai-machines/stories/{story_id}/assets/{asset_id}/talent/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        asset = get_object_or_404(StoryAsset, id=asset_id, story=story)
        
        if request.method == 'GET':
            assignments = AssetTalentAssignment.objects.filter(asset=asset)
            serializer = AssetTalentAssignmentSerializer(assignments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            data = request.data.copy()
            data['asset'] = asset.id
            serializer = AssetTalentAssignmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except (Story.DoesNotExist, StoryAsset.DoesNotExist):
        return Response(
            {'error': 'Story or Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing assignment: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def asset_talent_assignment_detail(request, assignment_id):
    """
    Update or delete asset talent assignment
    PUT /api/ai-machines/talent-assignments/asset/{id}/
    DELETE /api/ai-machines/talent-assignments/asset/{id}/
    """
    try:
        assignment = get_object_or_404(AssetTalentAssignment, id=assignment_id)
        # Verify user owns the story
        if assignment.asset.story.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'PUT':
            serializer = AssetTalentAssignmentSerializer(assignment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            assignment.delete()
            return Response({'message': 'Assignment deleted successfully'}, status=status.HTTP_200_OK)
            
    except AssetTalentAssignment.DoesNotExist:
        return Response(
            {'error': 'Assignment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing assignment: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Shot Talent Assignments ====================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def shot_talent_assignments(request, story_id, shot_id):
    """
    Get or create shot talent assignments
    GET /api/ai-machines/stories/{story_id}/shots/{shot_id}/talent/
    POST /api/ai-machines/stories/{story_id}/shots/{shot_id}/talent/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        shot = get_object_or_404(Shot, id=shot_id, story=story)
        
        if request.method == 'GET':
            assignments = ShotTalentAssignment.objects.filter(shot=shot)
            serializer = ShotTalentAssignmentSerializer(assignments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            data = request.data.copy()
            data['shot'] = shot.id
            serializer = ShotTalentAssignmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except (Story.DoesNotExist, Shot.DoesNotExist):
        return Response(
            {'error': 'Story or Shot not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing assignment: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def shot_talent_assignment_detail(request, assignment_id):
    """
    Update or delete shot talent assignment
    PUT /api/ai-machines/talent-assignments/shot/{id}/
    DELETE /api/ai-machines/talent-assignments/shot/{id}/
    """
    try:
        assignment = get_object_or_404(ShotTalentAssignment, id=assignment_id)
        # Verify user owns the story
        if assignment.shot.story.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'PUT':
            serializer = ShotTalentAssignmentSerializer(assignment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            assignment.delete()
            return Response({'message': 'Assignment deleted successfully'}, status=status.HTTP_200_OK)
            
    except ShotTalentAssignment.DoesNotExist:
        return Response(
            {'error': 'Assignment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing assignment: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




