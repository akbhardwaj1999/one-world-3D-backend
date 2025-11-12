from django.urls import path
from .views import parse_story

app_name = 'ai_machines'

urlpatterns = [
    path('parse-story/', parse_story, name='parse_story'),
]
