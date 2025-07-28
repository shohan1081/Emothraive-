from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from .prompt import PromptManager, TherapyType, ConversationStyle
from .pdf_processor import PDFVectorStore
from .models import TherapyChatMessage, TherapySession
from .serializers import TherapyChatMessageSerializer, TherapySessionSerializer, TherapySessionListSerializer
from openai import OpenAI
import logging
import os

logger = logging.getLogger(__name__)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.pdf_store = PDFVectorStore(folder_path=settings.PDF_FOLDER_PATH, vector_store_path=os.path.join(settings.BASE_DIR, 'vector_store'))
        self.prompt_manager = PromptManager(
            default_therapy_type=TherapyType.GENERAL,
            conversation_style=ConversationStyle.EMPATHETIC
        )
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        try:
            if not self.pdf_store.load_vector_store(allow_dangerous_deserialization=True):
                logger.info("Building vector store from PDFs...")
                self.pdf_store.build_vector_store()
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")

    def post(self, request, *args, **kwargs):
        user_message = request.data.get("message", "")
        session_id = request.data.get("session_id", None)

        if not user_message:
            return Response({"error": "Message cannot be empty"}, status=400)

        # Get or create session
        if session_id:
            try:
                session = TherapySession.objects.get(id=session_id, user=request.user)
            except TherapySession.DoesNotExist:
                return Response({"error": "Session not found or does not belong to user"}, status=404)
        else:
            # Create a new session if no session_id is provided
            session = TherapySession.objects.create(user=request.user, title=None) # Start with no title

        # Retrieve conversation history for this specific session
        conversation_history_db = TherapyChatMessage.objects.filter(session=session).order_by('timestamp')
        conversation_history = []
        for chat_message in conversation_history_db:
            conversation_history.append({"role": "user", "content": chat_message.user_message})
            conversation_history.append({"role": "assistant", "content": chat_message.ai_response})

        pdf_context = ""
        if self.pdf_store and self.pdf_store.vector_store:
            pdf_context = self.pdf_store.retrieve_pdf_context(user_message)

        messages = self.prompt_manager.create_conversation_messages(
            user_input=user_message,
            pdf_context=pdf_context,
            conversation_history=conversation_history
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                max_tokens=300
            )
            ai_response_text = response.choices[0].message.content

            # Save message to database, linked to the session
            TherapyChatMessage.objects.create(
                session=session,
                user_message=user_message,
                ai_response=ai_response_text
            )
            
            # If this is the first message in a new session, set the title
            if not session.title:
                # Use the first 50 characters of the user's message as the title
                session.title = user_message[:50] + ('...' if len(user_message) > 50 else '')
            
            # Update session's updated_at timestamp
            session.save()

            return Response({"success": True, "response": {"text": ai_response_text}, "session_id": str(session.id)})
        except Exception as e:
            logger.error(f"Error during OpenAI API call: {e}")
            return Response({"success": False, "error": str(e)}, status=500)

class TherapySessionViewSet(viewsets.ModelViewSet):
    queryset = TherapySession.objects.all()
    serializer_class = TherapySessionSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return TherapySessionListSerializer
        return TherapySessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TherapySession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        try:
            session = self.get_queryset().get(pk=pk)
            messages = session.messages.all()
            serializer = TherapyChatMessageSerializer(messages, many=True)
            return Response(serializer.data)
        except TherapySession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def clear_messages(self, request, pk=None):
        try:
            session = self.get_queryset().get(pk=pk)
            session.messages.all().delete()
            return Response({"success": True, "message": "Session messages cleared."},
                            status=status.HTTP_200_OK)
        except TherapySession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)