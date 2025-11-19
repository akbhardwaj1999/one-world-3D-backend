from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Chat
from .serializers import ChatSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_list(request):
    """
    Get all chats for the authenticated user
    GET /api/ai-machines/chats/
    """
    try:
        chats = Chat.objects.filter(user=request.user)
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': f'Error fetching chats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chat_create(request):
    """
    Create a new chat
    POST /api/ai-machines/chats/create/
    
    Body:
    {
        "title": "Chat Title" (optional, defaults to "New Chat")
    }
    """
    try:
        data = {
            'title': request.data.get('title', 'New Chat'),
            'messages': []
        }
        serializer = ChatSerializer(data=data)
        if serializer.is_valid():
            chat = serializer.save(user=request.user)
            return Response(ChatSerializer(chat).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': f'Error creating chat: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_detail(request, chat_id):
    """
    Get a specific chat
    GET /api/ai-machines/chats/{chat_id}/
    """
    try:
        chat = get_object_or_404(Chat, id=chat_id, user=request.user)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Chat.DoesNotExist:
        return Response(
            {'error': 'Chat not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error fetching chat: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def chat_update(request, chat_id):
    """
    Update a chat (title or messages)
    PUT/PATCH /api/ai-machines/chats/{chat_id}/update/
    
    Body:
    {
        "title": "Updated Title" (optional),
        "messages": [...] (optional)
    }
    """
    try:
        chat = get_object_or_404(Chat, id=chat_id, user=request.user)
        serializer = ChatSerializer(chat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Chat.DoesNotExist:
        return Response(
            {'error': 'Chat not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error updating chat: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def chat_delete(request, chat_id):
    """
    Delete a chat
    DELETE /api/ai-machines/chats/{chat_id}/delete/
    """
    try:
        chat = get_object_or_404(Chat, id=chat_id, user=request.user)
        chat.delete()
        return Response({'message': 'Chat deleted successfully'}, status=status.HTTP_200_OK)
    except Chat.DoesNotExist:
        return Response(
            {'error': 'Chat not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error deleting chat: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

