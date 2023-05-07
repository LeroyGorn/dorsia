

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from dorsia.settings import chroma_client, openai
from langchain import LLMChain, PromptTemplate
from langchain.schema import HumanMessage, AIMessage

from ai_assistant.memory_buffer import ConversationBufferMemory


class ChatView(View):
    memory = ConversationBufferMemory(memory_key="chat_history")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def construct_memory(self, user_id):
        user_conversation = chroma_client.get_or_create_collection(name=f'conversation_history_user_{user_id}')

        conversation_history = self.memory.chat_memory.messages
        restore_history = []
        print(user_conversation.get())
        print(user_conversation.get()['documents'])
        docs = user_conversation.get()['documents'][-50:]
        print(docs)
        if docs:
            for doc in docs:
                if docs.index(doc) % 2 == 0:
                    restore_history.append(AIMessage(content=doc, additional_kwargs={}, example=False))
                else:
                    restore_history.append(HumanMessage(content=doc, additional_kwargs={}, example=False))

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", memory_data=restore_history
        )

    def get(self, request):
        user_id = request.user.id
        self.construct_memory(user_id)
        return render(request, 'chat/chat.html')

    def post(self, request):
        question = request.POST.get('message')
        user_id = request.user.id
        user_conversation = chroma_client.get_or_create_collection(name=f'conversation_history_user_{user_id}')

        llm_chain = self.configure_ai()
        response = llm_chain.predict(question=question)

        self.fill_memory_buffer(user_conversation, user_id, question=question, answer=response)
        return JsonResponse({'response': response, 'question': question})

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
            memory=self.memory,
        )

    def fill_memory_buffer(self, user_conversation, user_id, question, answer):
        conversation_history = self.memory.chat_memory.messages
        if answer:
            user_conversation.add(
                documents=[question],
                metadatas=[{"source": "User"}],
                ids=[f"User_{len(conversation_history)-1}"],
            )
            user_conversation.add(
                documents=[answer],
                metadatas=[{"source": "AI"}],
                ids=[f"AI_{len(conversation_history)}"],
            )
