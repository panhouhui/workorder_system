from django.contrib import admin
from .models import Ticket, TicketLog


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'applicant', 'get_approvers', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'content', 'applicant__username', 'approver__username')

    def get_approvers(self, obj):
        return ", ".join([user.username for user in obj.approver.all()])
    get_approvers.short_description = "审批人"


@admin.register(TicketLog)
class TicketLogAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'action', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('ticket__title', 'user__username', 'action')
