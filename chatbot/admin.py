from django.contrib import admin
from .models import FAQCategory, FAQ, ChatSession, ChatMessage

@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['question', 'answer', 'keywords']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_ip', 'created_at', 'last_activity']
    readonly_fields = ['created_at', 'last_activity']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_preview', 'is_bot', 'timestamp', 'confidence']
    list_filter = ['is_bot', 'timestamp']
    readonly_fields = ['timestamp']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
