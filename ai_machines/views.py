from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from .models import Story, Character, Location, StoryAsset, Sequence, Shot
from .services.story_parser import parse_story_to_structured_data


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
        
        for asset_data in parsed_data.get('assets', []):
            StoryAsset.objects.create(
                story=story,
                name=asset_data.get('name', '')[:255],
                asset_type=asset_data.get('type', 'prop')[:50],
                description=asset_data.get('description', ''),
                complexity=asset_data.get('complexity', 'medium')[:20]
            )
        
        # Create sequences first
        sequences_dict = {}
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
            
            sequences_dict[seq_data.get('sequence_number', 1)] = sequence
        
        # Create shots and link to sequences
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
            
            # Link characters to shot
            char_names = shot_data.get('characters', [])
            if char_names:
                characters = Character.objects.filter(story=story, name__in=char_names)
                shot.characters.set(characters)
        
        return Response({
            'story_id': story.id,
            'parsed_data': parsed_data,
            'message': 'Story parsed successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error processing story: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
