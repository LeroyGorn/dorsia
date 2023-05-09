from ai_assistant.memory_buffer import ConversationBufferMemory
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from dorsia.settings import chroma_client, openai
from langchain import LLMChain, PromptTemplate
from langchain.schema import HumanMessage, AIMessage


class ChatView(TemplateView):
    template_name = "chat/chat.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        conversation_id = f"conversation_history_user_{self.request.user.id}"
        user_conversation = chroma_client.get_or_create_collection(name=conversation_id)

        docs = user_conversation.get()["documents"][-20:]
        cache.set(conversation_id, docs, timeout=3600)
        context["conversation_history"] = docs
        return context


class ChatResponseView(View):
    def configure_ai(self, memory):
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
            memory=memory
        )

    def construct_memory(self, docs):
        restore_history = [AIMessage(content=doc, additional_kwargs={}, example=False) if index % 2 == 0
                           else HumanMessage(content=doc, additional_kwargs={}, example=False) for index, doc in
                           enumerate(docs)]
        return ConversationBufferMemory(memory_key="chat_history", memory_data=restore_history)

    def post(self, request):
        question = request.POST.get("message")
        user_id = request.user.id
        conversation_id = f"conversation_history_user_{user_id}"
        user_conversation = chroma_client.get_or_create_collection(name=conversation_id)
        docs = cache.get(conversation_id)

        memory = self.construct_memory(docs)
        llm_chain = self.configure_ai(memory)

        response = llm_chain.predict(question=question)
        conversation_history = memory.chat_memory.messages
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
        return JsonResponse({"response": response, "question": question})
