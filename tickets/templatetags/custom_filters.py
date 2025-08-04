from django import template

register = template.Library()

@register.filter
def get_record_for_user(approval_records, user):
    return approval_records.filter(approver=user).first()
