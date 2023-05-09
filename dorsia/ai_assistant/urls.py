from ai_assistant.views import ChatView, ChatResponseView
from django.urls import path

urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("chat", ChatResponseView.as_view(), name="chat_message")
]
