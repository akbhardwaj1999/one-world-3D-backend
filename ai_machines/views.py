from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Story, Character, Location, StoryAsset, Sequence, Shot, ArtControlSettings, Chat, AssetImage, CharacterImage, LocationImage
from talent_pool.models import CharacterTalentAssignment, AssetTalentAssignment, ShotTalentAssignment
from .services.story_parser import parse_story_to_structured_data
from .services.cost_calculator import (
    calculate_asset_cost,
    calculate_shot_cost,
    calculate_sequence_cost,
    calculate_story_total_cost,
    get_budget_range
)
from .serializers import ArtControlSettingsSerializer, ChatSerializer


# ==================== Helper Functions ====================

def sync_story_parsed_data(story):
    """
    Sync story.parsed_data with current database state
    Updates characters, assets, locations, sequences in parsed_data
    """
    if not story.parsed_data:
        return
    
    parsed_data = story.parsed_data.copy()
    
    # Update characters in parsed_data
    if 'characters' in parsed_data:
        for char_data in parsed_data['characters']:
            char_id = char_data.get('id')
            if char_id:
                try:
                    db_char = Character.objects.get(id=char_id, story=story)
                    char_data['name'] = db_char.name
                    char_data['description'] = db_char.description
                    char_data['role'] = db_char.role
                    char_data['appearances'] = db_char.appearances
                except Character.DoesNotExist:
                    pass
    
    # Update assets in parsed_data
    if 'assets' in parsed_data:
        for asset_data in parsed_data['assets']:
            asset_id = asset_data.get('id')
            db_asset = None
            
            # Try to find asset by ID first
            if asset_id:
                try:
                    db_asset = StoryAsset.objects.get(id=asset_id, story=story)
                except StoryAsset.DoesNotExist:
                    pass
            
            # If not found by ID, try to find by name and type
            if not db_asset:
                asset_name = asset_data.get('name', '').strip()
                asset_type = asset_data.get('type', '').strip()
                if asset_name:
                    try:
                        # Try exact match first
                        db_asset = StoryAsset.objects.filter(
                            story=story,
                            name__iexact=asset_name
                        ).first()
                        
                        # If not found, try case-insensitive partial match
                        if not db_asset:
                            db_asset = StoryAsset.objects.filter(
                                story=story,
                                name__icontains=asset_name
                            ).first()
                        
                        # If still not found and type matches, try by type
                        if not db_asset and asset_type:
                            db_asset = StoryAsset.objects.filter(
                                story=story,
                                asset_type__iexact=asset_type
                            ).first()
                    except Exception:
                        pass
            
            # Update asset_data if found
            if db_asset:
                asset_data['id'] = db_asset.id
                asset_data['name'] = db_asset.name
                asset_data['description'] = db_asset.description
                asset_data['complexity'] = db_asset.complexity
                if db_asset.estimated_cost:
                    asset_data['estimated_cost'] = float(db_asset.estimated_cost)
    
    # Update locations in parsed_data
    if 'locations' in parsed_data:
        for loc_data in parsed_data['locations']:
            loc_id = loc_data.get('id')
            if loc_id:
                try:
                    db_location = Location.objects.get(id=loc_id, story=story)
                    loc_data['name'] = db_location.name
                    loc_data['description'] = db_location.description
                    loc_data['type'] = db_location.location_type
                    loc_data['scenes'] = db_location.scenes
                except Location.DoesNotExist:
                    pass
    
    # Update sequences in parsed_data
    if 'sequences' in parsed_data:
        for seq_data in parsed_data['sequences']:
            seq_id = seq_data.get('id')
            if seq_id:
                try:
                    db_sequence = Sequence.objects.get(id=seq_id, story=story)
                    seq_data['title'] = db_sequence.title
                    seq_data['description'] = db_sequence.description
                    if db_sequence.location:
                        seq_data['location'] = db_sequence.location.name
                    if db_sequence.estimated_time:
                        seq_data['estimated_time'] = db_sequence.estimated_time
                    if db_sequence.estimated_cost:
                        seq_data['estimated_cost'] = float(db_sequence.estimated_cost)
                    # Update characters in sequence
                    if 'characters' in seq_data:
                        seq_data['characters'] = [char.name for char in db_sequence.characters.all()]
                except Sequence.DoesNotExist:
                    pass
    
    # Save updated parsed_data
    story.parsed_data = parsed_data
    story.save(update_fields=['parsed_data'])


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
        characters_dict = {}  # Store characters by name for ID lookup
        for char_data in parsed_data.get('characters', []):
            character = Character.objects.create(
                story=story,
                name=char_data.get('name', '')[:255],
                description=char_data.get('description', ''),
                role=char_data.get('role', 'supporting')[:100],
                appearances=char_data.get('appearances', 0)
            )
            # Store character for ID lookup
            characters_dict[character.name] = character
        
        locations_dict = {}  # Store locations by name for ID lookup
        for loc_data in parsed_data.get('locations', []):
            location = Location.objects.create(
                story=story,
                name=loc_data.get('name', '')[:255],
                description=loc_data.get('description', ''),
                location_type=loc_data.get('type', 'outdoor')[:100],
                scenes=loc_data.get('scenes', 0)
            )
            # Store location for ID lookup
            locations_dict[location.name] = location
        
        # Create assets and calculate costs
        assets_dict = {}  # Store assets by name+type for ID lookup
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
            # Store asset for ID lookup
            asset_key = f"{asset.name}_{asset.asset_type}"
            assets_dict[asset_key] = asset
        
        # Create sequences first
        sequences_dict = {}
        sequences_with_ids = {}  #Store sequence objects with their IDs for later
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
        
        # Add IDs to characters - use the IDs we stored when creating them
        for char_data in enhanced_parsed_data.get('characters', []):
            char_name = char_data.get('name', '')
            if char_name in characters_dict:
                char_data['id'] = characters_dict[char_name].id
                print(f"DEBUG: Added ID {characters_dict[char_name].id} to character {char_name}")
        
        # Add IDs to locations - use the IDs we stored when creating them
        for loc_data in enhanced_parsed_data.get('locations', []):
            loc_name = loc_data.get('name', '')
            if loc_name in locations_dict:
                loc_data['id'] = locations_dict[loc_name].id
                print(f"DEBUG: Added ID {locations_dict[loc_name].id} to location {loc_name}")
        
        # Add IDs to assets - use the IDs we stored when creating them
        for asset_data in enhanced_parsed_data.get('assets', []):
            asset_name = asset_data.get('name', '')
            asset_type = asset_data.get('type', 'prop')
            asset_key = f"{asset_name}_{asset_type}"
            if asset_key in assets_dict:
                asset_data['id'] = assets_dict[asset_key].id
                if assets_dict[asset_key].estimated_cost:
                    asset_data['estimated_cost'] = float(assets_dict[asset_key].estimated_cost)
                print(f"DEBUG: Added ID {assets_dict[asset_key].id} to asset {asset_key}")
        
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
        
        # Add IDs and costs to assets in parsed data
        for asset in enhanced_parsed_data.get('assets', []):
            asset_name = asset.get('name', '')
            asset_type = asset.get('type', 'prop')
            asset_key = f"{asset_name}_{asset_type}"
            
            # Find the created asset
            asset_obj = assets_dict.get(asset_key)
            if not asset_obj:
                # Fallback: try to find in database
                asset_obj = StoryAsset.objects.filter(
                    story=story,
                    name=asset_name,
                    asset_type=asset_type
                ).first()
            
            if asset_obj:
                asset['id'] = asset_obj.id  # Add asset ID
                if asset_obj.estimated_cost:
                    asset['estimated_cost'] = float(asset_obj.estimated_cost)
        
        # Add IDs to locations in parsed data
        for location in enhanced_parsed_data.get('locations', []):
            location_name = location.get('name', '')
            
            # Find the created location
            location_obj = locations_dict.get(location_name)
            if not location_obj:
                # Fallback: try to find in database
                location_obj = Location.objects.filter(
                    story=story,
                    name=location_name
                ).first()
            
            if location_obj:
                location['id'] = location_obj.id  # Add location ID
        
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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def regenerate_story(request, story_id):
    """
    Regenerate story with updated character/asset/location data
    POST /api/ai-machines/stories/{story_id}/regenerate/
    
    This will:
    1. Get original story.raw_text
    2. Get updated data from database (characters, assets, locations)
    3. Create enhanced story text with updated descriptions
    4. Re-parse story with AI
    5. Update existing database records (preserve IDs)
    6. Update story.parsed_data
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        
        # Get original story text
        original_text = story.raw_text
        
        if not original_text:
            return Response(
                {'error': 'Story has no raw text to regenerate'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get updated data from database
        db_characters = Character.objects.filter(story=story)
        db_assets = StoryAsset.objects.filter(story=story)
        db_locations = Location.objects.filter(story=story)
        
        # Create enhanced story text with updated character/asset descriptions
        # This helps AI understand the updated context
        enhancement_parts = []
        
        if db_characters.exists():
            enhancement_parts.append("\n\nUPDATED CHARACTER INFORMATION:")
            for char in db_characters:
                enhancement_parts.append(
                    f"- {char.name}: {char.description} (Role: {char.role})"
                )
        
        if db_assets.exists():
            enhancement_parts.append("\n\nUPDATED ASSET INFORMATION:")
            for asset in db_assets:
                enhancement_parts.append(
                    f"- {asset.name} ({asset.asset_type}): {asset.description} (Complexity: {asset.complexity})"
                )
        
        if db_locations.exists():
            enhancement_parts.append("\n\nUPDATED LOCATION INFORMATION:")
            for loc in db_locations:
                enhancement_parts.append(
                    f"- {loc.name}: {loc.description} (Type: {loc.location_type})"
                )
        
        # Combine original text with enhancements
        enhanced_text = original_text + "\n\n" + "\n".join(enhancement_parts)
        
        # Re-parse story using AI with enhanced text
        parsed_data = parse_story_to_structured_data(enhanced_text)
        
        if 'error' in parsed_data and parsed_data.get('error'):
            return Response(
                {'error': parsed_data['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update story metadata
        story.title = parsed_data.get('summary', story.title)[:255]
        story.summary = parsed_data.get('summary', story.summary)
        story.total_shots = parsed_data.get('total_shots', story.total_shots)
        story.estimated_total_time = parsed_data.get('estimated_total_time', story.estimated_total_time)
        
        # Update existing characters (match by ID or name, preserve IDs)
        existing_characters = {c.id: c for c in db_characters}
        existing_characters_by_name = {c.name: c for c in db_characters}
        characters_dict = {}
        
        for char_data in parsed_data.get('characters', []):
            char_name = char_data.get('name', '').strip()
            if not char_name:
                continue
            
            # Try to find existing character by name (case-insensitive)
            existing_char = None
            for db_char in db_characters:
                if db_char.name.lower() == char_name.lower():
                    existing_char = db_char
                    break
            
            if existing_char:
                # Update existing character
                existing_char.name = char_name[:255]
                existing_char.description = char_data.get('description', existing_char.description)
                existing_char.role = char_data.get('role', existing_char.role)[:100]
                existing_char.appearances = char_data.get('appearances', existing_char.appearances)
                existing_char.save()
                characters_dict[char_name] = existing_char
            else:
                # Create new character if not found
                new_char = Character.objects.create(
                    story=story,
                    name=char_name[:255],
                    description=char_data.get('description', ''),
                    role=char_data.get('role', 'supporting')[:100],
                    appearances=char_data.get('appearances', 0)
                )
                characters_dict[char_name] = new_char
        
        # Update existing locations (match by name, preserve IDs)
        existing_locations_by_name = {loc.name: loc for loc in db_locations}
        locations_dict = {}
        
        for loc_data in parsed_data.get('locations', []):
            loc_name = loc_data.get('name', '').strip()
            if not loc_name:
                continue
            
            # Try to find existing location by name (case-insensitive)
            existing_loc = None
            for db_loc in db_locations:
                if db_loc.name.lower() == loc_name.lower():
                    existing_loc = db_loc
                    break
            
            if existing_loc:
                # Update existing location
                existing_loc.name = loc_name[:255]
                existing_loc.description = loc_data.get('description', existing_loc.description)
                existing_loc.location_type = loc_data.get('type', existing_loc.location_type)[:100]
                existing_loc.scenes = loc_data.get('scenes', existing_loc.scenes)
                existing_loc.save()
                locations_dict[loc_name] = existing_loc
            else:
                # Create new location if not found
                new_loc = Location.objects.create(
                    story=story,
                    name=loc_name[:255],
                    description=loc_data.get('description', ''),
                    location_type=loc_data.get('type', 'outdoor')[:100],
                    scenes=loc_data.get('scenes', 0)
                )
                locations_dict[loc_name] = new_loc
        
        # Update existing assets (match by name+type, preserve IDs)
        existing_assets_by_key = {}
        for asset in db_assets:
            key = f"{asset.name}_{asset.asset_type}".lower()
            existing_assets_by_key[key] = asset
        
        assets_dict = {}
        
        for asset_data in parsed_data.get('assets', []):
            asset_name = asset_data.get('name', '').strip()
            asset_type = asset_data.get('type', 'prop').strip()
            if not asset_name:
                continue
            
            asset_key = f"{asset_name}_{asset_type}".lower()
            
            # Try to find existing asset
            existing_asset = existing_assets_by_key.get(asset_key)
            
            if existing_asset:
                # Update existing asset
                existing_asset.name = asset_name[:255]
                existing_asset.description = asset_data.get('description', existing_asset.description)
                existing_asset.complexity = asset_data.get('complexity', existing_asset.complexity)[:20]
                existing_asset.estimated_cost = calculate_asset_cost(existing_asset)
                existing_asset.save()
                assets_dict[asset_key] = existing_asset
            else:
                # Create new asset if not found
                new_asset = StoryAsset.objects.create(
                    story=story,
                    name=asset_name[:255],
                    asset_type=asset_type[:50],
                    description=asset_data.get('description', ''),
                    complexity=asset_data.get('complexity', 'medium')[:20]
                )
                new_asset.estimated_cost = calculate_asset_cost(new_asset)
                new_asset.save()
                assets_dict[asset_key] = new_asset
        
        # Delete sequences and shots (we'll recreate them)
        # This ensures clean regeneration
        Shot.objects.filter(story=story).delete()
        Sequence.objects.filter(story=story).delete()
        
        # Recreate sequences
        sequences_dict = {}
        sequences_with_ids = {}
        
        for seq_data in parsed_data.get('sequences', []):
            location = None
            location_name = seq_data.get('location', '')
            if location_name and location_name in locations_dict:
                location = locations_dict[location_name]
            
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
                sequence_chars = []
                for char_name in char_names:
                    if char_name in characters_dict:
                        sequence_chars.append(characters_dict[char_name])
                sequence.characters.set(sequence_chars)
            
            seq_num = seq_data.get('sequence_number', 1)
            sequences_dict[seq_num] = sequence
            sequences_with_ids[seq_num] = sequence.id
        
        # Recreate shots
        shots_with_ids = {}
        
        for shot_data in parsed_data.get('shots', []):
            location = None
            location_name = shot_data.get('location', '')
            if location_name and location_name in locations_dict:
                location = locations_dict[location_name]
            
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
            
            shot.estimated_cost = calculate_shot_cost(shot)
            shot.save()
            
            # Link characters to shot
            char_names = shot_data.get('characters', [])
            if char_names:
                shot_chars = []
                for char_name in char_names:
                    if char_name in characters_dict:
                        shot_chars.append(characters_dict[char_name])
                shot.characters.set(shot_chars)
            
            shot_num = shot_data.get('shot_number', 1)
            shots_with_ids[shot_num] = shot.id
        
        # Calculate costs
        for sequence in sequences_dict.values():
            sequence.estimated_cost = calculate_sequence_cost(sequence)
            sequence.save()
        
        story.total_estimated_cost = calculate_story_total_cost(story)
        story.budget_range = get_budget_range(story.total_estimated_cost)
        
        # Update parsed_data with IDs and costs
        import copy
        enhanced_parsed_data = copy.deepcopy(parsed_data)
        
        # Add IDs to characters
        for char_data in enhanced_parsed_data.get('characters', []):
            char_name = char_data.get('name', '')
            if char_name in characters_dict:
                char_data['id'] = characters_dict[char_name].id
        
        # Add IDs to locations
        for loc_data in enhanced_parsed_data.get('locations', []):
            loc_name = loc_data.get('name', '')
            if loc_name in locations_dict:
                loc_data['id'] = locations_dict[loc_name].id
        
        # Add IDs to assets
        for asset_data in enhanced_parsed_data.get('assets', []):
            asset_name = asset_data.get('name', '')
            asset_type = asset_data.get('type', 'prop')
            asset_key = f"{asset_name}_{asset_type}".lower()
            if asset_key in assets_dict:
                asset_data['id'] = assets_dict[asset_key].id
                if assets_dict[asset_key].estimated_cost:
                    asset_data['estimated_cost'] = float(assets_dict[asset_key].estimated_cost)
        
        # Add IDs to sequences
        for seq in enhanced_parsed_data.get('sequences', []):
            seq_num = seq.get('sequence_number', 1)
            if seq_num in sequences_with_ids:
                seq['id'] = sequences_with_ids[seq_num]
        
        # Add IDs to shots
        for shot in enhanced_parsed_data.get('shots', []):
            shot_num = shot.get('shot_number', 1)
            if shot_num in shots_with_ids:
                shot['id'] = shots_with_ids[shot_num]
        
        # Add costs
        enhanced_parsed_data['total_estimated_cost'] = float(story.total_estimated_cost) if story.total_estimated_cost else None
        enhanced_parsed_data['budget_range'] = story.budget_range
        
        for shot in enhanced_parsed_data.get('shots', []):
            shot_obj = Shot.objects.filter(story=story, shot_number=shot.get('shot_number')).first()
            if shot_obj and shot_obj.estimated_cost:
                shot['estimated_cost'] = float(shot_obj.estimated_cost)
        
        for seq in enhanced_parsed_data.get('sequences', []):
            seq_obj = Sequence.objects.filter(story=story, sequence_number=seq.get('sequence_number')).first()
            if seq_obj and seq_obj.estimated_cost:
                seq['estimated_cost'] = float(seq_obj.estimated_cost)
        
        # Save updated parsed_data
        story.parsed_data = enhanced_parsed_data
        story.save()
        
        # Return updated story data
        story_data = {
            'id': story.id,
            'title': story.title,
            'raw_text': story.raw_text,
            'summary': story.summary,
            'parsed_data': enhanced_parsed_data,
            'total_shots': story.total_shots,
            'total_estimated_cost': float(story.total_estimated_cost) if story.total_estimated_cost else None,
            'budget_range': story.budget_range,
            'estimated_total_time': story.estimated_total_time,
            'created_at': story.created_at.isoformat() if story.created_at else None,
            'updated_at': story.updated_at.isoformat() if story.updated_at else None,
        }
        
        return Response({
            'message': 'Story regenerated successfully',
            'story': story_data
        }, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error regenerating story: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
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
        
        # Add IDs and costs to characters in parsed_data from database
        characters_in_parsed = parsed_data.get('characters', [])
        
        # Get all characters for this story to match by ID or name
        all_db_characters = {c.id: c for c in Character.objects.filter(story=story)}
        all_db_characters_list = list(all_db_characters.values())
        all_db_characters_by_name = {c.name: c for c in all_db_characters.values()}
        
        # Track which database characters have been assigned
        assigned_db_chars = set()
        
        for idx, char_data in enumerate(characters_in_parsed):
            # First check if ID already exists and verify it's still valid
            existing_id = char_data.get('id')
            if existing_id and existing_id in all_db_characters:
                # ID exists and is valid, update the data from database
                db_char = all_db_characters[existing_id]
                char_data['name'] = db_char.name
                char_data['description'] = db_char.description
                char_data['role'] = db_char.role
                char_data['appearances'] = db_char.appearances
                continue
            
            # If no valid ID, try to find by name
            char_name = char_data.get('name', '').strip()
            if not char_name:
                continue
            
            # Try exact match first
            db_character = all_db_characters_by_name.get(char_name)
            
            # If not found, try case-insensitive match
            if not db_character:
                for db_char in all_db_characters.values():
                    if db_char.name.lower() == char_name.lower():
                        db_character = db_char
                        break
            
            # If still not found, try partial match (in case name was updated)
            if not db_character:
                for db_char in all_db_characters.values():
                    # Check if either name contains the other
                    if (char_name.lower() in db_char.name.lower() or 
                        db_char.name.lower() in char_name.lower()):
                        db_character = db_char
                        break
            
            # Last resort: If only one character exists, use it
            if not db_character and len(all_db_characters) == 1:
                db_character = list(all_db_characters.values())[0]
            
            # If still not found and we have characters, use index-based matching
            # This handles cases where names don't match at all
            if not db_character and len(all_db_characters_list) > 0:
                # Try to match by index if same number of characters
                if len(characters_in_parsed) == len(all_db_characters_list):
                    # Use character at same index, but skip if already assigned
                    for db_char in all_db_characters_list:
                        if db_char.id not in assigned_db_chars:
                            db_character = db_char
                            break
                else:
                    # Use first available unassigned character
                    for db_char in all_db_characters_list:
                        if db_char.id not in assigned_db_chars:
                            db_character = db_char
                            break
            
            if db_character:
                char_data['id'] = db_character.id  # Add character ID
                assigned_db_chars.add(db_character.id)  # Mark as assigned
                # Also update other fields from database
                char_data['name'] = db_character.name
                char_data['description'] = db_character.description
                char_data['role'] = db_character.role
                char_data['appearances'] = db_character.appearances
        
        # Add IDs and costs to assets in parsed_data from database
        assets_in_parsed = parsed_data.get('assets', [])
        
        # Get all assets for this story to match by ID or name
        all_db_assets = {a.id: a for a in StoryAsset.objects.filter(story=story)}
        all_db_assets_list = list(all_db_assets.values())
        
        # Track which database assets have been assigned
        assigned_db_assets = set()
        
        for asset_data in assets_in_parsed:
            asset_id = asset_data.get('id')
            db_asset = None
            
            # First check if ID already exists and verify it's still valid
            if asset_id and asset_id in all_db_assets:
                # ID exists and is valid, update the data from database
                db_asset = all_db_assets[asset_id]
                asset_data['name'] = db_asset.name
                asset_data['description'] = db_asset.description
                asset_data['complexity'] = db_asset.complexity
                if db_asset.estimated_cost:
                    asset_data['estimated_cost'] = float(db_asset.estimated_cost)
                assigned_db_assets.add(db_asset.id)
                continue
            
            # If no valid ID, try to find by name and type
            asset_name = asset_data.get('name', '').strip()
            asset_type = asset_data.get('type', '').strip()
            
            if not asset_name:
                continue
            
            # Try exact match first (name + type)
            if asset_type:
                db_asset = StoryAsset.objects.filter(
                    story=story,
                    name__iexact=asset_name,
                    asset_type__iexact=asset_type
                ).exclude(id__in=assigned_db_assets).first()
            
            # If not found, try case-insensitive name match (ignore type)
            if not db_asset:
                db_asset = StoryAsset.objects.filter(
                    story=story,
                    name__iexact=asset_name
                ).exclude(id__in=assigned_db_assets).first()
            
            # If still not found, try partial name match
            if not db_asset:
                db_asset = StoryAsset.objects.filter(
                    story=story,
                    name__icontains=asset_name
                ).exclude(id__in=assigned_db_assets).first()
            
            # If still not found and type matches, try by type only
            if not db_asset and asset_type:
                db_asset = StoryAsset.objects.filter(
                    story=story,
                    asset_type__iexact=asset_type
                ).exclude(id__in=assigned_db_assets).first()
            
            # Last resort: use first available unassigned asset
            if not db_asset and len(all_db_assets_list) > 0:
                for db_asset_candidate in all_db_assets_list:
                    if db_asset_candidate.id not in assigned_db_assets:
                        db_asset = db_asset_candidate
                        break
            
            # Update asset_data if found
            if db_asset:
                asset_data['id'] = db_asset.id  # Add asset ID
                asset_data['name'] = db_asset.name
                asset_data['description'] = db_asset.description
                asset_data['complexity'] = db_asset.complexity
                if db_asset.estimated_cost:
                    asset_data['estimated_cost'] = float(db_asset.estimated_cost)
                assigned_db_assets.add(db_asset.id)
        
        # Add IDs to locations in parsed_data from database
        locations_in_parsed = parsed_data.get('locations', [])
        for loc_data in locations_in_parsed:
            # First check if ID already exists
            if loc_data.get('id'):
                continue
            
            loc_name = loc_data.get('name', '').strip()
            if not loc_name:
                continue
            
            # Find matching location in database (try exact match first, then case-insensitive)
            db_location = Location.objects.filter(
                story=story,
                name=loc_name
            ).first()
            
            # If not found, try case-insensitive match
            if not db_location:
                db_location = Location.objects.filter(
                    story=story,
                    name__iexact=loc_name
                ).first()
            
            if db_location:
                loc_data['id'] = db_location.id  # Add location ID
        
        # Add IDs and costs to shots in parsed_data from database
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
            
            if db_shot:
                shot_data['id'] = db_shot.id  # Add shot ID
                if db_shot.estimated_cost:
                    shot_data['estimated_cost'] = float(db_shot.estimated_cost)
        
        # Add IDs and costs to sequences in parsed_data from database
        sequences_in_parsed = parsed_data.get('sequences', [])
        for seq_data in sequences_in_parsed:
            seq_number = seq_data.get('sequence_number')
            if seq_number:
                db_sequence = Sequence.objects.filter(
                    story=story,
                    sequence_number=seq_number
                ).first()
                if db_sequence:
                    seq_data['id'] = db_sequence.id  # Add sequence ID
                    if db_sequence.estimated_cost:
                        seq_data['estimated_cost'] = float(db_sequence.estimated_cost)
        
        # Save updated parsed_data back to database (with IDs added)
        story.parsed_data = parsed_data
        story.save(update_fields=['parsed_data'])
        
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def story_cost_breakdown(request, story_id):
    """
    Get detailed cost breakdown for a story
    GET /api/ai-machines/stories/{story_id}/cost-breakdown/
    
    Returns:
    {
        "story_id": 1,
        "total_estimated_cost": 45600.00,
        "budget_range": "$40k-$50k",
        "breakdown": {
            "assets": {
                "total": 12000.00,
                "by_type": {
                    "model": 8000.00,
                    "prop": 2000.00,
                    "environment": 2000.00
                },
                "items": [
                    {
                        "name": "Asset Name",
                        "type": "model",
                        "complexity": "high",
                        "cost": 2000.00
                    }
                ]
            },
            "shots": {
                "total": 25000.00,
                "by_complexity": {
                    "low": 5000.00,
                    "medium": 10000.00,
                    "high": 10000.00
                },
                "items": [
                    {
                        "shot_number": 1,
                        "sequence_number": 1,
                        "complexity": "medium",
                        "estimated_time": "1-2 days",
                        "cost": 1500.00
                    }
                ]
            },
            "sequences": {
                "total": 25000.00,
                "items": [
                    {
                        "sequence_number": 1,
                        "title": "Sequence Title",
                        "cost": 10000.00,
                        "shot_count": 5
                    }
                ]
            }
        }
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        
        # Calculate asset breakdown
        assets_breakdown = {
            'total': 0.0,
            'by_type': {},
            'items': []
        }
        
        for asset in story.story_assets.all():
            cost = float(asset.estimated_cost) if asset.estimated_cost else 0.0
            assets_breakdown['total'] += cost
            asset_type = asset.asset_type.lower()
            assets_breakdown['by_type'][asset_type] = assets_breakdown['by_type'].get(asset_type, 0.0) + cost
            assets_breakdown['items'].append({
                'name': asset.name,
                'type': asset.asset_type,
                'complexity': asset.complexity,
                'cost': cost
            })
        
        # Calculate shots breakdown
        shots_breakdown = {
            'total': 0.0,
            'by_complexity': {},
            'items': []
        }
        
        for shot in story.shots.all():
            cost = float(shot.estimated_cost) if shot.estimated_cost else 0.0
            shots_breakdown['total'] += cost
            complexity = shot.complexity.lower()
            shots_breakdown['by_complexity'][complexity] = shots_breakdown['by_complexity'].get(complexity, 0.0) + cost
            shots_breakdown['items'].append({
                'shot_number': shot.shot_number,
                'sequence_number': shot.sequence.sequence_number if shot.sequence else None,
                'complexity': shot.complexity,
                'estimated_time': shot.estimated_time or 'N/A',
                'cost': cost
            })
        
        # Calculate sequences breakdown
        sequences_breakdown = {
            'total': 0.0,
            'items': []
        }
        
        for sequence in story.sequences.all():
            cost = float(sequence.estimated_cost) if sequence.estimated_cost else 0.0
            sequences_breakdown['total'] += cost
            sequences_breakdown['items'].append({
                'sequence_number': sequence.sequence_number,
                'title': sequence.title or f'Sequence {sequence.sequence_number}',
                'cost': cost,
                'shot_count': sequence.shots.count() if hasattr(sequence, 'shots') else 0
            })
        
        # Calculate talent costs breakdown
        talent_breakdown = {
            'total': 0.0,
            'by_type': {
                'voice_actor': 0.0,
                '3d_artist': 0.0,
                'animator': 0.0,
                'other': 0.0
            },
            'items': []
        }
        
        # Character talent assignments (voice actors)
        for character in story.characters.all():
            for assignment in character.talent_assignments.all():
                if assignment.rate_agreed:
                    cost = float(assignment.rate_agreed)
                    talent_breakdown['total'] += cost
                    talent_breakdown['by_type']['voice_actor'] += cost
                    talent_breakdown['items'].append({
                        'entity_type': 'character',
                        'entity_name': character.name,
                        'talent_name': assignment.talent.name,
                        'talent_type': 'voice_actor',
                        'role_type': assignment.role_type,
                        'cost': cost
                    })
        
        # Asset talent assignments (3D artists)
        for asset in story.story_assets.all():
            for assignment in asset.talent_assignments.all():
                cost = 0.0
                if assignment.rate_agreed:
                    if assignment.estimated_hours:
                        # Calculate: rate * hours
                        cost = float(assignment.rate_agreed) * float(assignment.estimated_hours)
                    else:
                        # Just use agreed rate as flat fee
                        cost = float(assignment.rate_agreed)
                    
                    if cost > 0:
                        talent_breakdown['total'] += cost
                        talent_type = assignment.talent.talent_type
                        if talent_type in ['3d_artist', 'modeler', 'texture_artist', 'rigger']:
                            talent_breakdown['by_type']['3d_artist'] += cost
                        else:
                            talent_breakdown['by_type']['other'] += cost
                        
                        talent_breakdown['items'].append({
                            'entity_type': 'asset',
                            'entity_name': asset.name,
                            'talent_name': assignment.talent.name,
                            'talent_type': talent_type,
                            'role_type': assignment.role_type,
                            'estimated_hours': assignment.estimated_hours,
                            'cost': cost
                        })
        
        # Shot talent assignments (animators)
        for shot in story.shots.all():
            for assignment in shot.talent_assignments.all():
                cost = 0.0
                if assignment.rate_agreed:
                    if assignment.estimated_hours:
                        # Calculate: rate * hours
                        cost = float(assignment.rate_agreed) * float(assignment.estimated_hours)
                    else:
                        # Just use agreed rate as flat fee
                        cost = float(assignment.rate_agreed)
                    
                    if cost > 0:
                        talent_breakdown['total'] += cost
                        talent_type = assignment.talent.talent_type
                        if talent_type in ['animator', 'lighting_artist', 'compositor', 'fx_artist']:
                            talent_breakdown['by_type']['animator'] += cost
                        else:
                            talent_breakdown['by_type']['other'] += cost
                        
                        talent_breakdown['items'].append({
                            'entity_type': 'shot',
                            'entity_name': f'Shot {shot.shot_number}',
                            'talent_name': assignment.talent.name,
                            'talent_type': talent_type,
                            'role_type': assignment.role_type,
                            'estimated_hours': assignment.estimated_hours,
                            'cost': cost
                        })
        
        # Calculate total cost including talent
        total_with_talent = float(story.total_estimated_cost) if story.total_estimated_cost else 0.0
        total_with_talent += talent_breakdown['total']
        
        response_data = {
            'story_id': story.id,
            'story_title': story.title,
            'total_estimated_cost': float(story.total_estimated_cost) if story.total_estimated_cost else 0.0,
            'total_with_talent_cost': total_with_talent,
            'budget_range': story.budget_range or None,
            'breakdown': {
                'assets': assets_breakdown,
                'shots': shots_breakdown,
                'sequences': sequences_breakdown,
                'talent': talent_breakdown
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error fetching cost breakdown: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
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
                    {'error': 'Art control settings already exist. Use PUT to upda,te.'},
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


# ==================== Asset Detail & Management APIs ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def asset_detail(request, story_id, asset_id):
    """
    Get asset details
    GET /api/ai-machines/stories/{story_id}/assets/{asset_id}/
    
    Returns:
    {
        "id": 1,
        "name": "Hero Character",
        "asset_type": "model",
        "description": "Main character model",
        "complexity": "high",
        "estimated_cost": 2000.00,
        "cost_per_hour": 100.00,
        "story_id": 1,
        "story_title": "My Story",
        "images": [
            {
                "id": 1,
                "image_url": "/media/assets/images/...",
                "image_type": "uploaded",
                "description": "",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        asset = get_object_or_404(StoryAsset, id=asset_id, story=story)
        
        # Get asset images
        images = AssetImage.objects.filter(asset=asset)
        images_data = []
        for img in images:
            images_data.append({
                'id': img.id,
                'image_url': request.build_absolute_uri(img.image.url) if img.image else None,
                'image_type': img.image_type,
                'description': img.description,
                'created_at': img.created_at.isoformat(),
            })
        
        asset_data = {
            'id': asset.id,
            'name': asset.name,
            'asset_type': asset.asset_type,
            'description': asset.description,
            'complexity': asset.complexity,
            'estimated_cost': float(asset.estimated_cost) if asset.estimated_cost else None,
            'cost_per_hour': float(asset.cost_per_hour) if asset.cost_per_hour else None,
            'story_id': story.id,
            'story_title': story.title,
            'images': images_data,
        }
        
        return Response(asset_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except StoryAsset.DoesNotExist:
        return Response(
            {'error': 'Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error fetching asset: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def asset_update(request, story_id, asset_id):
    """
    Update asset details (name, description, etc.)
    PATCH /api/ai-machines/stories/{story_id}/assets/{asset_id}/
    
    Body:
    {
        "name": "Updated Asset Name",
        "description": "Updated description",
        "complexity": "high"
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        asset = get_object_or_404(StoryAsset, id=asset_id, story=story)
        
        # Update fields if provided
        if 'name' in request.data:
            asset.name = request.data['name'][:255]
        if 'description' in request.data:
            asset.description = request.data['description']
        if 'complexity' in request.data:
            asset.complexity = request.data['complexity'][:20]
        
        asset.save()
        
        # Recalculate cost if complexity changed
        if 'complexity' in request.data:
            from .services.cost_calculator import calculate_asset_cost
            asset.estimated_cost = calculate_asset_cost(asset)
            asset.save()
        
        # Sync story.parsed_data with updated asset data
        sync_story_parsed_data(story)
        
        asset_data = {
            'id': asset.id,
            'name': asset.name,
            'asset_type': asset.asset_type,
            'description': asset.description,
            'complexity': asset.complexity,
            'estimated_cost': float(asset.estimated_cost) if asset.estimated_cost else None,
            'cost_per_hour': float(asset.cost_per_hour) if asset.cost_per_hour else None,
        }
        
        return Response(asset_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except StoryAsset.DoesNotExist:
        return Response(
            {'error': 'Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error updating asset: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def asset_upload_images(request, story_id, asset_id):
    """
    Upload images for an asset
    POST /api/ai-machines/stories/{story_id}/assets/{asset_id}/upload-images/
    
    Body (multipart/form-data):
    - images[]: file1, file2, ...
    - description: "Optional description"
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        asset = get_object_or_404(StoryAsset, id=asset_id, story=story)
        
        uploaded_files = request.FILES.getlist('images')
        description = request.data.get('description', '')
        
        if not uploaded_files:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image_file in uploaded_files:
            # Validate file type
            if not image_file.content_type.startswith('image/'):
                continue
            
            asset_image = AssetImage.objects.create(
                asset=asset,
                image=image_file,
                image_type='uploaded',
                description=description,
                uploaded_by=request.user
            )
            
            created_images.append({
                'id': asset_image.id,
                'image_url': request.build_absolute_uri(asset_image.image.url),
                'image_type': asset_image.image_type,
                'description': asset_image.description,
                'created_at': asset_image.created_at.isoformat(),
            })
        
        if not created_images:
            return Response(
                {'error': 'No valid images uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': f'Successfully uploaded {len(created_images)} image(s)',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except StoryAsset.DoesNotExist:
        return Response(
            {'error': 'Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error uploading images: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def asset_delete_image(request, story_id, asset_id, image_id):
    """
    Delete an asset image
    DELETE /api/ai-machines/stories/{story_id}/assets/{asset_id}/images/{image_id}/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        asset = get_object_or_404(StoryAsset, id=asset_id, story=story)
        image = get_object_or_404(AssetImage, id=image_id, asset=asset)
        
        image.delete()
        
        return Response({
            'message': 'Image deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except StoryAsset.DoesNotExist:
        return Response(
            {'error': 'Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except AssetImage.DoesNotExist:
        return Response(
            {'error': 'Image not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error deleting image: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Character Detail & Management APIs ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def character_detail(request, story_id, character_id):
    """
    Get character details
    GET /api/ai-machines/stories/{story_id}/characters/{character_id}/
    
    Returns:
    {
        "id": 1,
        "name": "Mara",
        "role": "protagonist",
        "description": "Main character...",
        "appearances": 10,
        "story_id": 1,
        "story_title": "My Story",
        "images": [...]
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        character = get_object_or_404(Character, id=character_id, story=story)
        
        # Get character images
        images = CharacterImage.objects.filter(character=character)
        images_data = []
        for img in images:
            images_data.append({
                'id': img.id,
                'image_url': request.build_absolute_uri(img.image.url) if img.image else None,
                'image_type': img.image_type,
                'description': img.description,
                'created_at': img.created_at.isoformat(),
            })
        
        character_data = {
            'id': character.id,
            'name': character.name,
            'role': character.role,
            'description': character.description,
            'appearances': character.appearances,
            'story_id': story.id,
            'story_title': story.title,
            'images': images_data,
        }
        
        return Response(character_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Character.DoesNotExist:
        return Response(
            {'error': 'Character not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error fetching character: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def character_update(request, story_id, character_id):
    """
    Update character details
    PATCH /api/ai-machines/stories/{story_id}/characters/{character_id}/
    
    Body:
    {
        "name": "Updated Name",
        "description": "Updated description",
        "role": "protagonist"
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        character = get_object_or_404(Character, id=character_id, story=story)
        
        # Update fields if provided
        if 'name' in request.data:
            character.name = request.data['name'][:255]
        if 'description' in request.data:
            character.description = request.data['description']
        if 'role' in request.data:
            character.role = request.data['role'][:100]
        
        character.save()
        
        # Sync story.parsed_data with updated character data
        sync_story_parsed_data(story)
        
        character_data = {
            'id': character.id,
            'name': character.name,
            'role': character.role,
            'description': character.description,
            'appearances': character.appearances,
        }
        
        return Response(character_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Character.DoesNotExist:
        return Response(
            {'error': 'Character not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error updating character: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def character_upload_images(request, story_id, character_id):
    """
    Upload images for a character
    POST /api/ai-machines/stories/{story_id}/characters/{character_id}/upload-images/
    
    Body (multipart/form-data):
    - images[]: file1, file2, ...
    - description: "Optional description"
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        character = get_object_or_404(Character, id=character_id, story=story)
        
        uploaded_files = request.FILES.getlist('images')
        description = request.data.get('description', '')
        
        if not uploaded_files:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image_file in uploaded_files:
            # Validate file type
            if not image_file.content_type.startswith('image/'):
                continue
            
            character_image = CharacterImage.objects.create(
                character=character,
                image=image_file,
                image_type='uploaded',
                description=description,
                uploaded_by=request.user
            )
            
            created_images.append({
                'id': character_image.id,
                'image_url': request.build_absolute_uri(character_image.image.url),
                'image_type': character_image.image_type,
                'description': character_image.description,
                'created_at': character_image.created_at.isoformat(),
            })
        
        if not created_images:
            return Response(
                {'error': 'No valid images uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': f'Successfully uploaded {len(created_images)} image(s)',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Character.DoesNotExist:
        return Response(
            {'error': 'Character not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error uploading images: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def character_delete_image(request, story_id, character_id, image_id):
    """
    Delete a character image
    DELETE /api/ai-machines/stories/{story_id}/characters/{character_id}/images/{image_id}/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        character = get_object_or_404(Character, id=character_id, story=story)
        image = get_object_or_404(CharacterImage, id=image_id, character=character)
        
        image.delete()
        
        return Response({
            'message': 'Image deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Character.DoesNotExist:
        return Response(
            {'error': 'Character not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except CharacterImage.DoesNotExist:
        return Response(
            {'error': 'Image not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error deleting image: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Location Detail & Management APIs ====================


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def location_detail(request, story_id, location_id):
    """
    Get location details
    GET /api/ai-machines/stories/{story_id}/locations/{location_id}/
    
    Returns:
    {
        "id": 1,
        "name": "Forest",
        "description": "A dark forest...",
        "location_type": "outdoor",
        "scenes": 5,
        "story_id": 1,
        "story_title": "My Story",
        "images": [...]
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        location = get_object_or_404(Location, id=location_id, story=story)
        
        # Get location images
        images = LocationImage.objects.filter(location=location)
        images_data = []
        for img in images:
            images_data.append({
                'id': img.id,
                'image_url': request.build_absolute_uri(img.image.url) if img.image else None,
                'image_type': img.image_type,
                'description': img.description,
                'created_at': img.created_at.isoformat(),
            })
        
        location_data = {
            'id': location.id,
            'name': location.name,
            'description': location.description,
            'location_type': location.location_type,
            'scenes': location.scenes,
            'story_id': story.id,
            'story_title': story.title,
            'images': images_data,
        }
        
        return Response(location_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Location.DoesNotExist:
        return Response(
            {'error': 'Location not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error fetching location: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def location_update(request, story_id, location_id):
    """
    Update location details
    PATCH /api/ai-machines/stories/{story_id}/locations/{location_id}/update/
    
    Body:
    {
        "name": "Updated Name",
        "description": "Updated description",
        "location_type": "indoor",
        "scenes": 10
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        location = get_object_or_404(Location, id=location_id, story=story)
        
        # Update fields if provided
        if 'name' in request.data:
            location.name = request.data['name'][:255]
        if 'description' in request.data:
            location.description = request.data['description']
        if 'location_type' in request.data:
            location.location_type = request.data['location_type'][:100]
        if 'scenes' in request.data:
            location.scenes = request.data['scenes']
        
        location.save()
        
        # Sync story.parsed_data with updated location data
        sync_story_parsed_data(story)
        
        location_data = {
            'id': location.id,
            'name': location.name,
            'description': location.description,
            'location_type': location.location_type,
            'scenes': location.scenes,
        }
        
        return Response(location_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Location.DoesNotExist:
        return Response(
            {'error': 'Location not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error updating location: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def location_upload_images(request, story_id, location_id):
    """
    Upload images for a location
    POST /api/ai-machines/stories/{story_id}/locations/{location_id}/upload-images/
    
    Body (multipart/form-data):
    - images[]: file1, file2, ...
    - description: "Optional description"
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        location = get_object_or_404(Location, id=location_id, story=story)
        
        uploaded_files = request.FILES.getlist('images')
        description = request.data.get('description', '')
        
        if not uploaded_files:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image_file in uploaded_files:
            # Validate file type
            if not image_file.content_type.startswith('image/'):
                continue
            
            location_image = LocationImage.objects.create(
                location=location,
                image=image_file,
                image_type='uploaded',
                description=description,
                uploaded_by=request.user
            )
            
            created_images.append({
                'id': location_image.id,
                'image_url': request.build_absolute_uri(location_image.image.url),
                'image_type': location_image.image_type,
                'description': location_image.description,
                'created_at': location_image.created_at.isoformat(),
            })
        
        if not created_images:
            return Response(
                {'error': 'No valid images uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': f'Successfully uploaded {len(created_images)} image(s)',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Location.DoesNotExist:
        return Response(
            {'error': 'Location not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error uploading images: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def location_delete_image(request, story_id, location_id, image_id):
    """
    Delete a location image
    DELETE /api/ai-machines/stories/{story_id}/locations/{location_id}/images/{image_id}/
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        location = get_object_or_404(Location, id=location_id, story=story)
        image = get_object_or_404(LocationImage, id=image_id, location=location)
        
        image.delete()
        
        return Response({
            'message': 'Image deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Location.DoesNotExist:
        return Response(
            {'error': 'Location not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except LocationImage.DoesNotExist:
        return Response(
            {'error': 'Image not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error deleting image: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Sequence Detail & Management APIs ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def sequence_detail(request, story_id, sequence_id):
    """
    Get sequence details
    GET /api/ai-machines/stories/{story_id}/sequences/{sequence_id}/
    
    Returns:
    {
        "id": 1,
        "sequence_number": 1,
        "title": "Opening Scene",
        "description": "The story begins...",
        "location": {"id": 1, "name": "Forest"},
        "characters": [{"id": 1, "name": "Hero"}],
        "estimated_time": "2-3 minutes",
        "total_shots": 5,
        "estimated_cost": 5000.00,
        "story_id": 1,
        "story_title": "My Story"
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        sequence = get_object_or_404(Sequence, id=sequence_id, story=story)
        
        # Get location data
        location_data = None
        if sequence.location:
            location_data = {
                'id': sequence.location.id,
                'name': sequence.location.name,
            }
        
        # Get characters data
        characters_data = []
        for char in sequence.characters.all():
            characters_data.append({
                'id': char.id,
                'name': char.name,
            })
        
        sequence_data = {
            'id': sequence.id,
            'sequence_number': sequence.sequence_number,
            'title': sequence.title,
            'description': sequence.description,
            'location': location_data,
            'characters': characters_data,
            'estimated_time': sequence.estimated_time,
            'total_shots': sequence.total_shots,
            'estimated_cost': float(sequence.estimated_cost) if sequence.estimated_cost else None,
            'story_id': story.id,
            'story_title': story.title,
        }
        
        return Response(sequence_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Sequence.DoesNotExist:
        return Response(
            {'error': 'Sequence not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error fetching sequence: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def sequence_update(request, story_id, sequence_id):
    """
    Update sequence details
    PATCH /api/ai-machines/stories/{story_id}/sequences/{sequence_id}/update/
    
    Body:
    {
        "title": "Updated Title",
        "description": "Updated description",
        "location_id": 1,
        "character_ids": [1, 2],
        "estimated_time": "3-4 minutes"
    }
    """
    try:
        story = get_object_or_404(Story, id=story_id, user=request.user)
        sequence = get_object_or_404(Sequence, id=sequence_id, story=story)
        
        # Update fields if provided
        if 'title' in request.data:
            sequence.title = request.data['title'][:255]
        if 'description' in request.data:
            sequence.description = request.data['description']
        if 'estimated_time' in request.data:
            sequence.estimated_time = request.data['estimated_time'][:100]
        
        # Update location if provided
        if 'location_id' in request.data:
            location_id = request.data['location_id']
            if location_id:
                location = Location.objects.filter(id=location_id, story=story).first()
                sequence.location = location
            else:
                sequence.location = None
        
        # Update characters if provided
        if 'character_ids' in request.data:
            character_ids = request.data['character_ids']
            characters = Character.objects.filter(id__in=character_ids, story=story)
            sequence.characters.set(characters)
        
        sequence.save()
        
        # Sync story.parsed_data with updated sequence data
        sync_story_parsed_data(story)
        
        # Get updated location and characters data
        location_data = None
        if sequence.location:
            location_data = {
                'id': sequence.location.id,
                'name': sequence.location.name,
            }
        
        characters_data = []
        for char in sequence.characters.all():
            characters_data.append({
                'id': char.id,
                'name': char.name,
            })
        
        sequence_data = {
            'id': sequence.id,
            'sequence_number': sequence.sequence_number,
            'title': sequence.title,
            'description': sequence.description,
            'location': location_data,
            'characters': characters_data,
            'estimated_time': sequence.estimated_time,
            'total_shots': sequence.total_shots,
            'estimated_cost': float(sequence.estimated_cost) if sequence.estimated_cost else None,
        }
        
        return Response(sequence_data, status=status.HTTP_200_OK)
        
    except Story.DoesNotExist:
        return Response(
            {'error': 'Story not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Sequence.DoesNotExist:
        return Response(
            {'error': 'Sequence not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response(
            {'error': f'Error updating sequence: {str(e)}', 'trace': error_trace if settings.DEBUG else None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
