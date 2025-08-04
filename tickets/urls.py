from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('create/', views.ticket_create, name='ticket_create'),
    path('<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('<int:pk>/approve/', views.ticket_approve, name='ticket_approve'),
    path('<int:pk>/pdf/', views.ticket_pdf, name='ticket_pdf'),
    path('api/status/', views.ticket_status_api, name='ticket_status_api'),
]
