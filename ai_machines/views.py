from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Story, Character, Location, StoryAsset, Sequence, Shot, ArtControlSettings, Chat
from .services.story_parser import parse_story_to_structured_data
from .services.cost_calculator import (
    calculate_asset_cost,
    calculate_shot_cost,
    calculate_sequence_cost,
    calculate_story_total_cost,
    get_budget_range
)
from .serializers import ArtControlSettingsSerializer, ChatSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def parse_story(request):
    """
    Parse story text and extract structured data
    POST /api/ai-machines/parse-story/
    
    Body:
    {
        "story_text": "story content here..."
    }
    """
    try:
        story_text = request.data.get('story_text', '').strip()
        
        if not story_text:
            return Response(
                {'error': 'story_text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse story using AI
        parsed_data = parse_story_to_structured_data(story_text)
        
        if 'error' in parsed_data and parsed_data.get('error'):
            return Response(
                {'error': parsed_data['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Save story to database
        story = Story.objects.create(
            user=request.user,
            title=parsed_data.get('summary', 'Untitled Story')[:255],
            raw_text=story_text,
            parsed_data=parsed_data,
            summary=parsed_data.get('summary', ''),
            total_shots=parsed_data.get('total_shots', 0),
            estimated_total_time=parsed_data.get('estimated_total_time', '')
        )
        
        # Create related objects
        for char_data in parsed_data.get('characters', []):
            Character.objects.create(
                story=story,
                name=char_data.get('name', '')[:255],
                description=char_data.get('description', ''),
                role=char_data.get('role', 'supporting')[:100],
                appearances=char_data.get('appearances', 0)
            )
        
        for loc_data in parsed_data.get('locations', []):
            Location.objects.create(
                story=story,
                name=loc_data.get('name', '')[:255],
                description=loc_data.get('description', ''),
                location_type=loc_data.get('type', 'outdoor')[:100],
                scenes=loc_data.get('scenes', 0)
            )
        
        # Create assets and calculate costs
        for asset_data in parsed_data.get('assets', []):
            asset = StoryAsset.objects.create(
                story=story,
                name=asset_data.get('name', '')[:255],
                asset_type=asset_data.get('type', 'prop')[:50],
                description=asset_data.get('description', ''),
                complexity=asset_data.get('complexity', 'medium')[:20]
            )
            # Calculate and save asset cost
            asset.estimated_cost = calculate_asset_cost(asset)
            asset.save()
        
        # Create sequences first
        sequences_dict = {}
        sequences_with_ids = {}  # Store sequence objects with their IDs for later
        for seq_data in parsed_data.get('sequences', []):
            location = None
            location_name = seq_data.get('location', '')
            if location_name:
                location = Location.objects.filter(story=story, name=location_name).first()
            
            sequence = Sequence.objects.create(
                story=story,
                sequence_number=seq_data.get('sequence_number', 1),
                title=seq_data.get('title', '')[:255],
                description=seq_data.get('description', ''),
                location=location,
                estimated_time=seq_data.get('estimated_time', '')[:100],
                total_shots=seq_data.get('total_shots', 0)
            )
            
            # Link characters to sequence
            char_names = seq_data.get('characters', [])
            if char_names:
                characters = Character.objects.filter(story=story, name__in=char_names)
                sequence.characters.set(characters)
            
            seq_num = seq_data.get('sequence_number', 1)
            sequences_dict[seq_num] = sequence
            sequences_with_ids[seq_num] = sequence.id  # Store the ID directly
        
        # Create shots and link to sequences
        shots_with_ids = {}  # Store shot objects with their IDs for later
        for shot_data in parsed_data.get('shots', []):
            location = None
            location_name = shot_data.get('location', '')
            if location_name:
                location = Location.objects.filter(story=story, name=location_name).first()
            
            # Link shot to sequence
            sequence = None
            sequence_number = shot_data.get('sequence_number')
            if sequence_number and sequence_number in sequences_dict:
                sequence = sequences_dict[sequence_number]
            
            shot = Shot.objects.create(
                story=story,
                sequence=sequence,
                shot_number=shot_data.get('shot_number', 1),
                description=shot_data.get('description', ''),
                location=location,
                camera_angle=shot_data.get('camera_angle', '')[:100],
                complexity=shot_data.get('complexity', 'medium')[:20],
                estimated_time=shot_data.get('estimated_time', '')[:100],
                special_requirements=shot_data.get('special_requirements', [])
            )
            
            # Calculate and save shot cost
            shot.estimated_cost = calculate_shot_cost(shot)
            shot.save()
            
            # Link characters to shot
            char_names = shot_data.get('characters', [])
            if char_names:
                characters = Character.objects.filter(story=story, name__in=char_names)
                shot.characters.set(characters)
            
            shot_num = shot_data.get('shot_number', 1)
            shots_with_ids[shot_num] = shot.id  # Store the ID directly
        
        # Add sequence and shot IDs to parsed data for frontend navigation
        # Use the IDs we just created instead of querying the database
        import copy
        enhanced_parsed_data = copy.deepcopy(parsed_data)
        
        # Add IDs to sequences - use the IDs we stored when creating them
        for seq in enhanced_parsed_data.get('sequences', []):
            seq_num = seq.get('sequence_number', 1)
            # Try multiple type conversions to ensure we find the match
            seq_id = None
            if seq_num in sequences_with_ids:
                seq_id = sequences_with_ids[seq_num]
            elif int(seq_num) in sequences_with_ids:
                seq_id = sequences_with_ids[int(seq_num)]
            elif str(seq_num) in sequences_with_ids:
                seq_id = sequences_with_ids[str(seq_num)]
            
            if seq_id:
                seq['id'] = seq_id
                print(f"DEBUG: Added ID {seq_id} to sequence {seq_num}")
            else:
                print(f"DEBUG: WARNING - Could not find ID for sequence {seq_num} (type: {type(seq_num)}). Available keys: {list(sequences_with_ids.keys())}")
        
        # Add IDs to shots - use the IDs we stored when creating them
        for shot in enhanced_parsed_data.get('shots', []):
            shot_num = shot.get('shot_number', 1)
            # Try multiple type conversions to ensure we find the match
            shot_id = None
            if shot_num in shots_with_ids:
                shot_id = shots_with_ids[shot_num]
            elif int(shot_num) in shots_with_ids:
                shot_id = shots_with_ids[int(shot_num)]
            elif str(shot_num) in shots_with_ids:
                shot_id = shots_with_ids[str(shot_num)]
            
            if shot_id:
                shot['id'] = shot_id
                print(f"DEBUG: Added ID {shot_id} to shot {shot_num}")
            else:
                print(f"DEBUG: WARNING - Could not find ID for shot {shot_num} (type: {type(shot_num)}). Available keys: {list(shots_with_ids.keys())}")
        
        # Debug: Print what IDs we're adding (for immediate visibility)
        print(f"DEBUG: sequences_with_ids = {sequences_with_ids}")
        print(f"DEBUG: shots_with_ids = {shots_with_ids}")
        print(f"DEBUG: enhanced_parsed_data sequences = {[s.get('sequence_number') for s in enhanced_parsed_data.get('sequences', [])]}")
        print(f"DEBUG: enhanced_parsed_data shots = {[s.get('shot_number') for s in enhanced_parsed_data.get('shots', [])]}")
        
        # Check if IDs were actually added to enhanced_parsed_data
        sequences_with_ids_check = [s.get('id') for s in enhanced_parsed_data.get('sequences', []) if s.get('id')]
        shots_with_ids_check = [s.get('id') for s in enhanced_parsed_data.get('shots', []) if s.get('id')]
        print(f"DEBUG: Sequences in enhanced_parsed_data WITH IDs: {sequences_with_ids_check}")
        print(f"DEBUG: Shots in enhanced_parsed_data WITH IDs: {shots_with_ids_check}")
        
        # Convert dictionary keys to strings for JSON serialization
        # JSON requires string keys, so convert int keys to strings
        sequence_ids_str = {str(k): v for k, v in sequences_with_ids.items()}
        shot_ids_str = {str(k): v for k, v in shots_with_ids.items()}
        
        print(f"DEBUG: sequence_ids_str (after string conversion) = {sequence_ids_str}")
        print(f"DEBUG: shot_ids_str (after string conversion) = {shot_ids_str}")
        
        # Calculate costs for sequences (sum of shot costs)
        for sequence in sequences_dict.values():
            sequence.estimated_cost = calculate_sequence_cost(sequence)
            sequence.save()
        
        # Calculate total story cost and budget range
        story.total_estimated_cost = calculate_story_total_cost(story)
        story.budget_range = get_budget_range(story.total_estimated_cost)
        story.save()
        
        # Add cost information to enhanced_parsed_data for frontend
        enhanced_parsed_data['total_estimated_cost'] = float(story.total_estimated_cost) if story.total_estimated_cost else None
        enhanced_parsed_data['budget_range'] = story.budget_range
        
        # Add costs to assets in parsed data
        for asset in enhanced_parsed_data.get('assets', []):
            asset_obj = StoryAsset.objects.filter(story=story, name=asset.get('name', '')).first()
            if asset_obj and asset_obj.estimated_cost:
                asset['estimated_cost'] = float(asset_obj.estimated_cost)
        
        # Add costs to shots in parsed data 
        for shot in enhanced_parsed_data.get('shots', []):
            shot_obj = Shot.objects.filter(story=story, shot_number=shot.get('shot_number')).first()
            if shot_obj and shot_obj.estimated_cost:
                shot['estimated_cost'] = float(shot_obj.estimated_cost)
        
        # Add costs to sequences in parsed data
        for seq in enhanced_parsed_data.get('sequences', []):
            seq_obj = Sequence.objects.filter(story=story, sequence_number=seq.get('sequence_number')).first()
            if seq_obj and seq_obj.estimated_cost:
                seq['estimated_cost'] = float(seq_obj.estimated_cost)
        
        # Also add IDs at top level for easier access (like story_id)
        response_data = {
            'story_id': story.id,
            'parsed_data': enhanced_parsed_data,
            'message': 'Story parsed successfully',
            'sequence_ids': sequence_ids_str,  # Map of sequence_number (string) -> id
            'shot_ids': shot_ids_str,  # Map of shot_number (string) -> id
        }
        
        print(f"DEBUG: response_data sequence_ids = {response_data['sequence_ids']}")
        print(f"DEBUG: response_data shot_ids = {response_data['shot_ids']}")
        print(f"DEBUG: response_data['parsed_data']['sequences'] with IDs = {[(s.get('sequence_number'), s.get('id')) for s in response_data['parsed_data'].get('sequences', [])]}")
        print(f"DEBUG: response_data['parsed_data']['shots'] with IDs = {[(s.get('shot_number'), s.get('id')) for s in response_data['parsed_data'].get('shots', [])]}")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing story: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def story_list(request):
    """
    Get all stories for the authenticated user
    GET /api/ai-machines/stories/
    
    Returns:
    {
        "stories": [
            {
                "id": 1,
                "title": "Story Title",
                "summary": "Story summary...",
                "total_shots": 10,
                "total_estimated_cost": 45600.00,
                "budget_range": "$40k-$50k",
                "estimated_total_time": "2-3 weeks",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
    """
    try:
        stories = Story.objects.filter(user=request.user).order_by('-updated_at')
        
        stories_data = []
        for story in stories:
            stories_data.append({
                'id': story.id,
                'title': story.title,
                'summary': story.summary[:200] if story.summary else '',  # First 200 chars
                'total_shots': story.total_shots,
                'total_estimated_cost': float(story.total_estimated_cost) if story.total_estimated_cost else None,
                'budget_range': story.budget_range or None,
                'estimated_total_time': story.estimated_total_time or None,
                'created_at': story.created_at.isoformat() if story.created_at else None,
                'updated_at': story.updated_at.isoformat() if story.updated_at else None,
            })
        
        return Response({
            'stories': stories_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error fetching stories: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def story_detail(request, story_id):
    """
    Get a single story by ID for the authenticated user
    GET /api/ai-machines/stories/{story_id}/
    
    Returns:
    {
        "id": 1,
        "title": "Story Title",
        "summary": "Story summary...",
        "parsed_data": {...},
        "total_shots": 10,
        "total_estimated_cost": 45600.00,
        "budget_range": "$40k-$50k",
        "estimated_total_time": "2-3 weeks",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        
        # Get parsed_data and enhance it with cost information from database
        parsed_data = story.parsed_data.copy() if story.parsed_data else {}
        
        # Add cost information to parsed_data if missing (for old stories)
        # Add total cost and budget range
        if story.total_estimated_cost:
            parsed_data['total_estimated_cost'] = float(story.total_estimated_cost)
        if story.budget_range:
            parsed_data['budget_range'] = story.budget_range
        
        # Add costs to assets in parsed_data from database
        assets_in_parsed = parsed_data.get('assets', [])
        for asset_data in assets_in_parsed:
            asset_name = asset_data.get('name', '')
            asset_type = asset_data.get('type', '')
            # Find matching asset in database
            db_asset = StoryAsset.objects.filter(
                story=story,
                name=asset_name,
                asset_type=asset_type
            ).first()
            if db_asset and db_asset.estimated_cost:
                asset_data['estimated_cost'] = float(db_asset.estimated_cost)
        
        # Add costs to shots in parsed_data from database
        shots_in_parsed = parsed_data.get('shots', [])
        for shot_data in shots_in_parsed:
            shot_number = shot_data.get('shot_number')
            sequence_number = shot_data.get('sequence_number')
            # Find matching shot in database
            db_shot = None
            if shot_number and sequence_number:
                # Try to find by sequence and shot number
                sequence = Sequence.objects.filter(
                    story=story,
                    sequence_number=sequence_number
                ).first()
                if sequence:
                    db_shot = Shot.objects.filter(
                        sequence=sequence,
                        shot_number=shot_number
                    ).first()
            elif shot_number:
                # Fallback: find by shot number only
                db_shot = Shot.objects.filter(
                    story=story,
                    shot_number=shot_number
                ).first()
            
            if db_shot and db_shot.estimated_cost:
                shot_data['estimated_cost'] = float(db_shot.estimated_cost)
        
        # Add costs to sequences in parsed_data from database
        sequences_in_parsed = parsed_data.get('sequences', [])
        for seq_data in sequences_in_parsed:
            seq_number = seq_data.get('sequence_number')
            if seq_number:
                db_sequence = Sequence.objects.filter(
                    story=story,
                    sequence_number=seq_number
                ).first()
                if db_sequence and db_sequence.estimated_cost:
                    seq_data['estimated_cost'] = float(db_sequence.estimated_cost)
        
        story_data = {
            'id': story.id,
            'title': story.title,
            'raw_text': story.raw_text or '',  # Original story text
            'summary': story.summary or '',
            'parsed_data': parsed_data,  # Enhanced parsed_data with costs
            'total_shots': story.total_shots,
            'total_estimated_cost': float(story.total_estimated_cost) if story.total_estimated_cost else None,
            'budget_range': story.budget_range or None,
            'estimated_total_time': story.estimated_total_time or None,
            'created_at': story.created_at.isoformat() if story.created_at else None,
            'updated_at': story.updated_at.isoformat() if story.updated_at else None,
        }
        
        return Response(story_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error fetching story: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def art_control_settings(request, story_id):
    """
    Get, create, or update art control settings for a story
    GET /api/ai-machines/stories/{story_id}/art-control/
    POST /api/ai-machines/stories/{story_id}/art-control/
    PUT /api/ai-machines/stories/{story_id}/art-control/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        
        if request.method == 'GET':
            # Get existing settings or return defaults
            art_control, created = ArtControlSettings.objects.get_or_create(
                story=story,
                defaults={'created_by': request.user}
            )
            serializer = ArtControlSettingsSerializer(art_control)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            # Create new settings
            if ArtControlSettings.objects.filter(story=story).exists():
                return Response(
                    {'error': 'Art control settings already exist. Use PUT to update.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ArtControlSettingsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(story=story, created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PUT':
            # Update existing settings
            art_control, created = ArtControlSettings.objects.get_or_create(
                story=story,
                defaults={'created_by': request.user}
            )
            serializer = ArtControlSettingsSerializer(art_control, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing art control settings: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def reset_art_control_settings(request, story_id):
    """
    Reset art control settings to defaults
    DELETE /api/ai-machines/stories/{story_id}/art-control/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        art_control = get_object_or_404(ArtControlSettings, story=story)
        
        # Reset to defaults by deleting and recreating
        art_control.delete()
        new_art_control = ArtControlSettings.objects.create(
            story=story,
            created_by=request.user
        )
        serializer = ArtControlSettingsSerializer(new_art_control)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ArtControlSettings.DoesNotExist:
        return Response(
            {'error': 'Art control settings not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error resetting art control settings: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def merge_art_control_settings(*settings_objects):
    """
    Merge art control settings with inheritance.
    Lower level settings override higher level settings.
    Missing values are inherited from higher levels.
    """
    if not settings_objects:
        return {}
    
    # Start with the first (highest level) settings
    merged = {}
    serializer = ArtControlSettingsSerializer(settings_objects[0])
    merged = serializer.data.copy()
    
    # Override with lower level settings (skip None/empty values for inheritance)
    for settings_obj in settings_objects[1:]:
        serializer = ArtControlSettingsSerializer(settings_obj)
        data = serializer.data
        
        # Merge: lower level overrides higher level if value exists
        for key, value in data.items():
            # Skip metadata fields
            if key in ['id', 'created_at', 'updated_at', 'story_id', 'story_title', 'sequence_id', 'shot_id']:
                continue
            
            # For JSON fields (lists), merge if not empty
            if isinstance(value, list):
                if value:  # If list has items, use it
                    merged[key] = value
            # For string fields that can be None (atmosphere, time_of_day, shot_duration)
            # Special handling: if value is explicitly None, it means "no restriction" - don't inherit
            elif key in ['atmosphere', 'time_of_day', 'shot_duration']:
                if value is None:
                    # Explicitly set to None means "no restriction" - override inheritance
                    merged[key] = None
                elif value != '':
                    # Has a specific value - use it
                    merged[key] = value
                # If empty string, inherit from higher level (don't override)
            # For other string fields, use if not None and not empty
            elif value is not None and value != '':
                merged[key] = value
            # For boolean fields, always use the value
            elif isinstance(value, bool):
                merged[key] = value
    
    return merged


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def sequence_art_control_settings(request, story_id, sequence_id):
    """
    Get, create, or update art control settings for a sequence
    GET /api/ai-machines/stories/{story_id}/sequences/{sequence_id}/art-control/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        sequence = get_object_or_404(Sequence, id=sequence_id, story=story)
        
        if request.method == 'GET':
            # Get story-level settings (for inheritance)
            story_settings, _ = ArtControlSettings.objects.get_or_create(
                story=story,
                defaults={'created_by': request.user}
            )
            
            # Get sequence-level settings
            sequence_settings, created = ArtControlSettings.objects.get_or_create(
                sequence=sequence,
                defaults={'created_by': request.user}
            )
            
            # Merge with inheritance: story -> sequence
            merged_data = merge_art_control_settings(story_settings, sequence_settings)
            
            # Add metadata
            merged_data['id'] = sequence_settings.id
            merged_data['sequence_id'] = sequence.id
            merged_data['story_id'] = story.id
            merged_data['story_title'] = story.title
            
            return Response(merged_data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            if ArtControlSettings.objects.filter(sequence=sequence).exists():
                return Response(
                    {'error': 'Art control settings already exist. Use PUT to update.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ArtControlSettingsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(sequence=sequence, created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PUT':
            art_control, created = ArtControlSettings.objects.get_or_create(
                sequence=sequence,
                defaults={'created_by': request.user}
            )
            serializer = ArtControlSettingsSerializer(art_control, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except (Story.DoesNotExist, Sequence.DoesNotExist):
        return Response(
            {'error': 'Story or Sequence not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing art control settings: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def shot_art_control_settings(request, story_id, shot_id):
    """
    Get, create, or update art control settings for a shot
    GET /api/ai-machines/stories/{story_id}/shots/{shot_id}/art-control/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        shot = get_object_or_404(Shot, id=shot_id, story=story)
        
        if request.method == 'GET':
            # Get story-level settings (for inheritance)
            story_settings, _ = ArtControlSettings.objects.get_or_create(
                story=story,
                defaults={'created_by': request.user}
            )
            
            # Get sequence-level settings (if shot has a sequence)
            sequence_settings = None
            if shot.sequence:
                sequence_settings, _ = ArtControlSettings.objects.get_or_create(
                    sequence=shot.sequence,
                    defaults={'created_by': request.user}
                )
            
            # Get shot-level settings
            shot_settings, created = ArtControlSettings.objects.get_or_create(
                shot=shot,
                defaults={'created_by': request.user}
            )
            
            # Merge with inheritance: story -> sequence -> shot
            if sequence_settings:
                merged_data = merge_art_control_settings(story_settings, sequence_settings, shot_settings)
            else:
                merged_data = merge_art_control_settings(story_settings, shot_settings)
            
            # Add metadata
            merged_data['id'] = shot_settings.id
            merged_data['shot_id'] = shot.id
            merged_data['story_id'] = story.id
            merged_data['story_title'] = story.title
            if shot.sequence:
                merged_data['sequence_id'] = shot.sequence.id
            
            return Response(merged_data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            if ArtControlSettings.objects.filter(shot=shot).exists():
                return Response(
                    {'error': 'Art control settings already exist. Use PUT to update.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ArtControlSettingsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(shot=shot, created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PUT':
            art_control, created = ArtControlSettings.objects.get_or_create(
                shot=shot,
                defaults={'created_by': request.user}
            )
            serializer = ArtControlSettingsSerializer(art_control, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
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
            {'error': f'Error processing art control settings: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
