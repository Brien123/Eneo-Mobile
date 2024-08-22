from django.contrib import admin
from .models import User, Messages
# Register your models here.

admin.site.register(User)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'read_status', 'created_at')
    list_filter = ('read_status', 'created_at')
    search_fields = ('user__username', 'message')

    def message_preview(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')

    message_preview.short_description = 'Message Preview'

admin.site.register(Messages, MessagesAdmin)