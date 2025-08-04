import tempfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from reportlab.pdfbase import pdfmetrics
from django.db.models import Q

from .models import Ticket, TicketLog
from .forms import TicketCreateForm, TicketApproveForm
from reportlab.pdfgen import canvas
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from .models import Ticket
from .models import ApprovalRecord
from docx import Document
from django.http import HttpResponse
import tempfile
import os
from docx2pdf import convert

@login_required
def ticket_list(request):
    user = request.user

    if user.role == 'employee':
        tickets = Ticket.objects.filter(applicant=user).order_by('-created_at')


    elif user.role == 'approver':

        tickets = Ticket.objects.filter(

            Q(applicant=user) | Q(approval_records__approver=user)

        ).distinct().order_by('-created_at')


    else:  # admin
        tickets = Ticket.objects.all().order_by('-created_at')

    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    logs = ticket.logs.all().order_by('timestamp')

    # 改为判断是否有审批记录并且状态是 pending
    try:
        record = ApprovalRecord.objects.get(ticket=ticket, approver=request.user)
        can_approve = record.status == 'pending'
    except ApprovalRecord.DoesNotExist:
        can_approve = False

    form = None

    if can_approve:
        if request.method == 'POST':
            form = TicketApproveForm(request.POST)
            if form.is_valid():
                record.status = form.cleaned_data['status']
                record.opinion = form.cleaned_data['opinion']
                record.save()

                TicketLog.objects.create(
                    ticket=ticket,
                    user=request.user,
                    action=f'审批{record.get_status_display()}',
                    message=record.opinion or ''
                )

                # 更新 ticket 总状态
                records = ticket.approval_records.all()
                if records.filter(status='rejected').exists():
                    ticket.status = 'rejected'
                elif records.filter(status='pending').exists():
                    ticket.status = 'pending'
                else:
                    ticket.status = 'approved'
                ticket.save()

                messages.success(request, '审批成功')
                return redirect('tickets:ticket_list')
        else:
            form = TicketApproveForm(initial={'status': 'approved', 'opinion': ''})

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'logs': logs,
        'form': form,
        'can_approve': can_approve
    })


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.applicant = request.user
            ticket.status = 'pending'
            ticket.save()
            form.save_m2m()

            # 为每个审批人创建审批记录
            for approver in form.cleaned_data['approver']:
                ApprovalRecord.objects.create(ticket=ticket, approver=approver)

            return redirect('tickets:ticket_list')
    else:
        form = TicketCreateForm(user=request.user)

    return render(request, 'tickets/ticket_create.html', {'form': form})

@login_required
def ticket_approve(request, pk):

    ticket = get_object_or_404(Ticket, pk=pk)

    try:
        record = ApprovalRecord.objects.get(ticket=ticket, approver=request.user)
    except ApprovalRecord.DoesNotExist:
        messages.error(request, '您不是此工单的审批人。')
        return redirect('tickets:ticket_list')

    if record.status != 'pending':
        messages.info(request, '您已完成审批。')
        return redirect('tickets:ticket_list')

    if request.method == 'POST':
        form = TicketApproveForm(request.POST)
        if form.is_valid():
            record.status = form.cleaned_data['status']
            record.opinion = form.cleaned_data['opinion']
            record.save()

            TicketLog.objects.create(
                ticket=ticket,
                user=request.user,
                action=f"审批{record.get_status_display()}",
                message=record.opinion or ''
            )

            # 更新工单总体状态
            records = ticket.approval_records.all()
            if records.filter(status='rejected').exists():
                ticket.status = 'rejected'
            elif records.filter(status='pending').exists():
                ticket.status = 'pending'
            else:
                ticket.status = 'approved'
            ticket.save()

            messages.success(request, f"审批已提交，当前工单状态为：{ticket.get_status_display()}")
            return redirect('tickets:ticket_list')

    else:
        form = TicketApproveForm(initial={'status': 'approved', 'opinion': ''})

    return render(request, 'tickets/ticket_approve.html', {
        'ticket': ticket,
        'form': form
    })


# 需要一个系统中存在的中文字体，比如 Windows 的宋体 (SimSun)  要不然会有乱码
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))

@login_required
@login_required
def ticket_pdf(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    template_path = r"F:\chrome下载内容\工单模板.docx"  # 注意路径中的 r

    doc = Document(template_path)

    # 要填充的数据
    data_map = {
        "【作业类型】": "高空作业（≥2米）",  # 可以从 ticket 读取
        "【作业地点】": getattr(ticket, "location", "未设置"),
        "开始时间：": ticket.start_time.strftime("%Y-%m-%d %H:%M") if ticket.start_time else "未设置",
        "结束时间：": ticket.end_time.strftime("%Y-%m-%d %H:%M") if ticket.end_time else "未设置",
        "负责人：": ticket.leader if hasattr(ticket, "leader") else "未设置",
        "作业人员：": ticket.workers if hasattr(ticket, "workers") else "未设置",
        "【作业内容】": ticket.content,
        "【审批意见】": ticket.opinion or "无",
    }

    # 遍历段落并替换对应字段
    paragraphs = doc.paragraphs
    for i, para in enumerate(paragraphs):
        for key, val in data_map.items():
            if para.text.strip().startswith(key):
                if key.endswith("：") or key.endswith(":"):
                    para.text = f"{key} {val}"
                else:
                    # 下一段填入内容
                    if i + 1 < len(paragraphs):
                        paragraphs[i + 1].text = str(val)

    # 保存 Word 临时文件
    tmp_doc = tempfile.mktemp(suffix='.docx')
    doc.save(tmp_doc)

    # 转换为 PDF
    tmp_pdf = tempfile.mktemp(suffix='.pdf')
    convert(tmp_doc, tmp_pdf)

    with open(tmp_pdf, 'rb') as f:
        pdf_data = f.read()

    # 清理临时文件
    os.remove(tmp_doc)
    os.remove(tmp_pdf)

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.pk}.pdf"'
    return response


#实时更新工单的状态
@login_required
def ticket_status_api(request):
    tickets = Ticket.objects.filter(applicant=request.user).prefetch_related('approval_records', 'approver')
    data = []
    for ticket in tickets:
        approval_statuses = [
            {'approver': r.approver.username, 'status': r.status}
            for r in ticket.approval_records.all()
        ]
        data.append({
            'id': ticket.id,
            'status': ticket.status,
            'approval_records': approval_statuses,
        })
    return JsonResponse({'tickets': data})