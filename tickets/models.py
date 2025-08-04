from datetime import timezone

from django.db import models
from accounts.models import User

class Ticket(models.Model):
    TICKET_TYPE_CHOICES = [
        ('明火作业', '明火作业'),
        ('高空作业', '高空作业'),
        ('雾化作业', '雾化作业'),
        ('动火作业', '动火作业'),
        ('冷工作业', '冷工作业'),
        ('电气作业', '电气作业'),
        ('起重吊装作业', '起重吊装作业')
    ]

    title = models.CharField(max_length=50, choices=TICKET_TYPE_CHOICES, verbose_name="工单类型")
    location = models.CharField(max_length=200, verbose_name="作业地点", default="本厂区")
    start_time = models.DateTimeField(verbose_name="开始时间",blank=True, null=True)
    end_time = models.DateTimeField(verbose_name='结束时间', blank=True, null=True)
    leader = models.CharField(max_length=50, verbose_name="负责人", default='未指定')
    workers = models.TextField(verbose_name="作业人员",blank=True, null=True)  # 多人逗号分隔
    content = models.TextField(verbose_name="作业内容",blank=True, null=True)
    protection_measures = models.TextField(verbose_name="安全防护措施",blank=True, null=True)
    emergency_measures = models.TextField(verbose_name="应急措施", default="无")
    attention = models.TextField(verbose_name="注意事项", default="注意安全")
    attachments = models.TextField(blank=True, null=True, verbose_name="附件")

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', verbose_name="申请人")
    approver = models.ManyToManyField(User, related_name='approvals', verbose_name="审批人")

    status = models.CharField(max_length=20, choices=[
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '被驳回'),
        ('archived', '已归档')
    ], default='pending', verbose_name="状态")

    opinion = models.TextField(blank=True, null=True, verbose_name="审批意见")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.get_title_display()} - {self.get_status_display()}"


class TicketLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user.username} - {self.action}"

class ApprovalRecord(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='approval_records')
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('pending', '待审批'), ('approved', '已通过'), ('rejected', '驳回')],
        default='pending'
    )
    opinion = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)  # 新增字段：审批顺序

    class Meta:
        unique_together = ('ticket', 'approver')
        ordering = ['order']  # 默认按顺序排列
