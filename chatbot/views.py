from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import uuid
from datetime import datetime

from .models import ChatSession, ChatMessage
from .utils.response_generator import ResponseGenerator

class ChatView(View):
    def get(self, request):
        return render(request, 'chatbot/chat.html')
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)
            
            # Get or create session
            if session_id:
                try:
                    session = ChatSession.objects.get(session_id=session_id)
                except ChatSession.DoesNotExist:
                    session = None
            else:
                session = None
            
            if not session:
                session_id = str(uuid.uuid4())
                session = ChatSession.objects.create(
                    session_id=session_id,
                    user_ip=self.get_client_ip(request)
                )
            
            # Save user message
            user_msg = ChatMessage.objects.create(
                session=session,
                message=user_message,
                is_bot=False
            )
            
            # Generate response
            response_generator = ResponseGenerator()
            bot_response, confidence, category = response_generator.generate_response(user_message)
            
            # Save bot response
            bot_msg = ChatMessage.objects.create(
                session=session,
                message=bot_response,
                is_bot=True,
                confidence=confidence
            )
            
            return JsonResponse({
                'response': bot_response,
                'session_id': session.session_id,
                'confidence': confidence,
                'category': category
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

def index(request):
    return render(request, 'chatbot/index.html')
