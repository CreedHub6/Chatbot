from django.db import models
from django.contrib.auth.models import User

class FAQCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class FAQ(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    keywords = models.TextField(help_text="Comma-separated keywords for matching")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.question[:50] + "..."

class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
