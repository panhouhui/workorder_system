from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
    path('', RedirectView.as_view(url='/login/', permanent=False)),  # 首页自动跳转到 /login/
    path('', include('accounts.urls')),  # 允许 accounts 的 login/ logout/ register/
    path('tickets/', include('tickets.urls')),
]
