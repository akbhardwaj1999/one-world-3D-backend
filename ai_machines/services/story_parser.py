"""
Story Parser Service
Uses OpenAI GPT-4 to parse story/script text into structured data
"""
from openai import OpenAI
import json
import os
from django.conf import settings

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY', getattr(settings, 'OPENAI_API_KEY', None))
client = OpenAI(api_key=api_key) if api_key else None


def parse_story_to_structured_data(story_text):
    """
    Parse story text and extract structured data:
    - Characters
    - Locations
    - Assets
    - Shots with complexity
    
    Args:
        story_text (str): The story/script text to parse
        
    Returns:
        dict: Structured data with characters, locations, assets, shots
    """
    if not story_text or not story_text.strip():
        return {
            "error": "Story text is empty",
            "characters": [],
            "locations": [],
            "assets": [],
            "shots": []
        }
    
    if not client:
        return {
            "error": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
            "characters": [],
            "locations": [],
            "assets": [],
            "shots": []
        }
    
    prompt = f"""You are a professional script analyzer for 3D production and animation.

Analyze this story/script and extract structured data in JSON format:

{story_text}

Return a JSON object with this exact structure:
{{
    "characters": [
        {{
            "name": "character name",
            "description": "physical and personality description",
            "role": "protagonist/antagonist/supporting",
            "appearances": number of times character appears
        }}
    ],
    "locations": [
        {{
            "name": "location name",
            "description": "detailed location description",
            "type": "indoor/outdoor/fantasy/sci-fi/realistic",
            "scenes": number of scenes in this location
        }}
    ],
    "assets": [
        {{
            "name": "asset name",
            "type": "model/prop/environment/effect",
            "description": "what this asset is",
            "complexity": "low/medium/high"
        }}
    ],
    "shots": [
        {{
            "shot_number": 1,
            "description": "what happens in this shot",
            "characters": ["character names"],
            "location": "location name",
            "camera_angle": "close-up/wide/medium/etc",
            "complexity": "low/medium/high",
            "estimated_time": "time estimate like '1-2 days'",
            "special_requirements": ["any special effects or requirements"]
        }}
    ],
    "summary": "brief summary of the story",
    "total_shots": number,
    "estimated_total_time": "overall time estimate"
}}

Be thorough and extract all details. Return ONLY valid JSON, no additional text."""

    try:
        # Use OpenAI Chat API
        # Try with response_format first (for models that support it)
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # Using gpt-4o which supports structured outputs
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional script analyzer for 3D production. Always return valid JSON only, no markdown, no code blocks. Return ONLY the JSON object, nothing else."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
        except Exception as e:
            # Fallback: Try without response_format (for models that don't support it)
            if "response_format" in str(e) or "not supported" in str(e).lower():
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional script analyzer for 3D production. Always return valid JSON only, no markdown, no code blocks. Return ONLY the JSON object, nothing else."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=4000
                )
            else:
                raise e
        
        # Parse JSON response
        result_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith("```json"):
            result_text = result_text[7:]  # Remove ```json
        if result_text.startswith("```"):
            result_text = result_text[3:]  # Remove ```
        if result_text.endswith("```"):
            result_text = result_text[:-3]  # Remove closing ```
        result_text = result_text.strip()
        
        result = json.loads(result_text)
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse JSON response: {str(e)}",
            "characters": [],
            "locations": [],
            "assets": [],
            "shots": []
        }
    except Exception as e:
        return {
            "error": f"Error parsing story: {str(e)}",
            "characters": [],
            "locations": [],
            "assets": [],
            "shots": []
        }
