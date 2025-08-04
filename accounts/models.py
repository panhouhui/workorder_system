from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('employee', '员工'),
        ('approver', '审批人'),
        ('admin', '管理员'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def is_employee(self):
        return self.role == 'employee'

    def is_approver(self):
        return self.role == 'approver'


    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return f"{self.username}（{self.get_role_display()}）"