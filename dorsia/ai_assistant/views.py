import chromadb
from chromadb.config import Settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from dorsia.settings import DB_DIR
from dorsia.settings import openai
from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory


class ChatView(TemplateView):
    template_name = "chat/chat.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        conversation_id = f"conversation_history_user_{self.request.user.id}"
        docs = cache.get(conversation_id)

        if not docs:
            chroma_client = chromadb.Client(Settings(
                chroma_api_impl="rest",
                chroma_server_host="dorsia_container",
                chroma_server_http_port="8000",
                persist_directory=DB_DIR
            ))
            user_conversation = chroma_client.get_or_create_collection(name=conversation_id)
            docs = user_conversation.get()["documents"][-20:]
            cache.set(conversation_id, docs, timeout=3600)
            docs = docs if docs else ['']

        context["conversation_history"] = docs
        return context


class ChatResponseView(View):
    def configure_ai(self):
        template = """
        {chat_history}
        Human: {question}
        AI:
        """
        prompt_template = PromptTemplate(input_variables=["chat_history", "question"], template=template)
        return LLMChain(
            llm=openai,
            prompt=prompt_template,
            verbose=True,
            memory=ConversationBufferMemory(memory_key="chat_history")
        )

    def post(self, request):
        chroma_client = chromadb.Client(Settings(
            chroma_api_impl="rest",
            chroma_server_host="dorsia_container",
            chroma_server_http_port="8000",
            persist_directory=DB_DIR
        ))
        question = request.POST.get("message")
        user_id = request.user.id
        conversation_id = f"conversation_history_user_{user_id}"
        user_conversation = chroma_client.get_or_create_collection(name=conversation_id)

        llm_chain = self.configure_ai()
        response = llm_chain.predict(question=question)

        conversation_history = llm_chain.memory.chat_memory.messages
        if response:
            user_conversation.add(
                documents=[question],
                metadatas=[{"source": "User"}],
                ids=[f"User_{len(conversation_history)-1}"],
            )
            user_conversation.add(
                documents=[response],
                metadatas=[{"source": "AI"}],
                ids=[f"AI_{len(conversation_history)}"],
            )

        docs = user_conversation.get()["documents"][-20:]
        cache.set(conversation_id, docs, timeout=3600)

        chroma_client.persist()
        return JsonResponse({"response": response})
