from django import forms
from .models import Ticket
from accounts.models import User

class TicketCreateForm(forms.ModelForm):
    approver = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="选择审批人"
    )

    class Meta:
        model = Ticket
        fields = [
            'title',
            'location',
            'start_time',
            'end_time',
            'leader',
            'workers',
            'content',
            'protection_measures',
            'emergency_measures',
            'attention',
            'attachments',
            'approver',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['approver'].queryset = User.objects.filter(role='approver').exclude(id=user.id)


class TicketApproveForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'opinion']
        widgets = {
            'status': forms.Select(choices=[('approved', '通过'), ('rejected', '驳回')]),
            'opinion': forms.Textarea(attrs={'rows': 4}),
        }