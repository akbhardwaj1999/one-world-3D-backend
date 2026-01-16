from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Department, StoryDepartment,
    AssetDepartmentAssignment, ShotDepartmentAssignment,
)
from .serializers import (
    DepartmentSerializer, StoryDepartmentSerializer,
    AssetDepartmentAssignmentSerializer, ShotDepartmentAssignmentSerializer,
)
from ai_machines.models import Story, StoryAsset, Shot


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def department_list_create(request):
    """
    List all departments or create a new department
    GET /api/departments/
    POST /api/departments/
    """
    if request.method == 'GET':
        departments = Department.objects.filter(is_active=True).order_by('display_order', 'name')
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def department_detail(request, department_id):
    """
    Get, update, or delete a department
    GET /api/departments/{id}/
    PUT /api/departments/{id}/
    DELETE /api/departments/{id}/
    """
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'GET':
        serializer = DepartmentSerializer(department)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        department.delete()
        return Response({'message': 'Department deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def story_departments(request, story_id):
    """
    Get departments for a story or assign a department to a story
    GET /api/departments/stories/{story_id}/
    POST /api/departments/stories/{story_id}/
    """
    story = get_object_or_404(Story, id=story_id, user=request.user)
    
    if request.method == 'GET':
        story_departments = StoryDepartment.objects.filter(story=story)
        serializer = StoryDepartmentSerializer(story_departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        department_id = request.data.get('department')
        if not department_id:
            return Response(
                {'error': 'department is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        department = get_object_or_404(Department, id=department_id)
        
        # Check if already assigned
        if StoryDepartment.objects.filter(story=story, department=department).exists():
            return Response(
                {'error': 'Department already assigned to this story'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        story_dept = StoryDepartment.objects.create(
            story=story,
            department=department,
            assigned_by=request.user,
            notes=request.data.get('notes', '')
        )
        serializer = StoryDepartmentSerializer(story_dept) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def story_department_remove(request, story_id, department_id):
    """
    Remove a department from a story
    DELETE /api/departments/stories/{story_id}/{department_id}/
    """
    story = get_object_or_404(Story, id=story_id, user=request.user)
    story_dept = get_object_or_404(StoryDepartment, story=story, department_id=department_id)
    story_dept.delete()
    return Response({'message': 'Department removed from story'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def asset_department_assignments(request, story_id, asset_id):
    """
    Get or create asset department assignments
    GET /api/departments/stories/{story_id}/assets/{asset_id}/
    POST /api/departments/stories/{story_id}/assets/{asset_id}/
    """
    story = get_object_or_404(Story, id=story_id, user=request.user)
    asset = get_object_or_404(StoryAsset, id=asset_id, story=story)
    
    if request.method == 'GET':
        assignments = AssetDepartmentAssignment.objects.filter(asset=asset)
        serializer = AssetDepartmentAssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        department_id = request.data.get('department')
        if not department_id:
            return Response(
                {'error': 'department is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        department = get_object_or_404(Department, id=department_id)
        
        # Check if already assigned
        existing = AssetDepartmentAssignment.objects.filter(asset=asset, department=department).first()
        if existing:
            # Update existing assignment
            serializer = AssetDepartmentAssignmentSerializer(existing, data=request.data, partial=True)
        else:
            # Create new assignment
            serializer = AssetDepartmentAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(asset=asset, department=department, assigned_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def asset_department_assignment_detail(request, assignment_id):
    """
    Update or delete asset department assignment
    PUT /api/departments/assignments/asset/{assignment_id}/
    DELETE /api/departments/assignments/asset/{assignment_id}/
    """
    assignment = get_object_or_404(AssetDepartmentAssignment, id=assignment_id)
    
    # Check if user owns the story
    if assignment.asset.story.user != request.user:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'PUT':
        serializer = AssetDepartmentAssignmentSerializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        assignment.delete()
        return Response({'message': 'Assignment deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def shot_department_assignments(request, story_id, shot_id):
    """
    Get or create shot department assignments
    GET /api/departments/stories/{story_id}/shots/{shot_id}/
    POST /api/departments/stories/{story_id}/shots/{shot_id}/ll
    """
    story = get_object_or_404(Story, id=story_id, user=request.user)
    shot = get_object_or_404(Shot, id=shot_id, story=story)
    
    if request.method == 'GET':
        assignments = ShotDepartmentAssignment.objects.filter(shot=shot)
        serializer = ShotDepartmentAssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        department_id = request.data.get('department')
        if not department_id:
            return Response(
                {'error': 'department is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        department = get_object_or_404(Department, id=department_id)
        
        # Check if already assigned
        existing = ShotDepartmentAssignment.objects.filter(shot=shot, department=department).first()
        if existing:
            # Update existing assignment
            serializer = ShotDepartmentAssignmentSerializer(existing, data=request.data, partial=True)
        else:
            # Create new assignment
            serializer = ShotDepartmentAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(shot=shot, department=department, assigned_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def shot_department_assignment_detail(request, assignment_id):
    """
    Update or delete shot department assignment
    PUT /api/departments/assignments/shot/{assignment_id}/
    DELETE /api/departments/assignments/shot/{assignment_id}/
    """
    assignment = get_object_or_404(ShotDepartmentAssignment, id=assignment_id)
    
    # Check if user owns the story
    if assignment.shot.story.user != request.user:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'PUT':
        serializer = ShotDepartmentAssignmentSerializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        assignment.delete()
        return Response({'message': 'Assignment deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def department_stats(request, story_id, department_id):
    """
    Get statistics for a department in a story
    GET /api/departments/stories/{story_id}/{department_id}/stats/
    """
    story = get_object_or_404(Story, id=story_id, user=request.user)
    department = get_object_or_404(Department, id=department_id)
    
    # Get asset assignments
    asset_assignments = AssetDepartmentAssignment.objects.filter(
        asset__story=story,
        department=department
    )
    
    # Get shot assignments
    shot_assignments = ShotDepartmentAssignment.objects.filter(
        shot__story=story,
        department=department
    )
    
    # Calculate costs
    from decimal import Decimal
    total_cost = Decimal('0.00')
    asset_cost = Decimal('0.00')
    shot_cost = Decimal('0.00')
    
    # Calculate asset costs
    for assignment in asset_assignments.select_related('asset'):
        if assignment.asset.estimated_cost:
            asset_cost += Decimal(str(assignment.asset.estimated_cost))
    
    # Calculate shot costs
    for assignment in shot_assignments.select_related('shot'):
        if assignment.shot.estimated_cost:
            shot_cost += Decimal(str(assignment.shot.estimated_cost))
    
    total_cost = asset_cost + shot_cost
    
    # Calculate statistics
    stats = {
        'department': {
            'id': department.id,
            'name': department.name,
            'type': department.department_type,
        },
        'assets': {
            'total': asset_assignments.count(),
            'by_status': {
                status: asset_assignments.filter(status=status).count()
                for status, _ in AssetDepartmentAssignment.STATUS_CHOICES
            },
            'by_priority': {
                priority: asset_assignments.filter(priority=priority).count()
                for priority, _ in AssetDepartmentAssignment.PRIORITY_CHOICES
            },
        },
        'shots': {
            'total': shot_assignments.count(),
            'by_status': {
                status: shot_assignments.filter(status=status).count()
                for status, _ in ShotDepartmentAssignment.STATUS_CHOICES
            },
            'by_priority': {
                priority: shot_assignments.filter(priority=priority).count()
                for priority, _ in ShotDepartmentAssignment.PRIORITY_CHOICES
            },
        },
        'overdue': {
            'assets': asset_assignments.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).count(),
            'shots': shot_assignments.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']


            ).count(),
        },
        'costs': {
            'total': float(total_cost),
            'assets': float(asset_cost),
            'shots': float(shot_cost),
        }
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def department_assets(request, story_id, department_id):
    """
    Get all assets assigned to a department in a story
    GET /api/departments/stories/{story_id}/{department_id}/assets/
    """
    story = get_object_or_404(Story, id=story_id, user=request.user)
    department = get_object_or_404(Department, id=department_id)
    
    assignments = AssetDepartmentAssignment.objects.filter(
        asset__story=story,
        department=department
    ).select_related('asset', 'department')
    
    serializer = AssetDepartmentAssignmentSerializer(assignments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def department_shots(request, story_id, department_id):
    """
    Get all shots assigned to a department in a story
    GET /api/departments/stories/{story_id}/{department_id}/shots/
    """
    story = get_object_or_404(Story, id=story_id, user=request.user)
    department = get_object_or_404(Department, id=department_id)
    
    assignments = ShotDepartmentAssignment.objects.filter(
        shot__story=story,
        department=department
    ).select_related('shot', 'department')
    
    serializer = ShotDepartmentAssignmentSerializer(assignments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
