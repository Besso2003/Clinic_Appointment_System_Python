from django.contrib import admin
from .models import ConsultationRecord
# Register your models here.

@admin.register(ConsultationRecord)
class ConsultationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'diagnosis', 'created_at')
    search_fields = ('diagnosis', 'notes', 'prescription', 'requested_tests')
    list_filter = ('created_at',)
