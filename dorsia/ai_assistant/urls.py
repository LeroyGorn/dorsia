from django.urls import path

from ai_assistant.views import ChatView

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
]
