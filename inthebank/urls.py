from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
	path('', TemplateView.as_view(template_name='homepage.html'),name='homepage-index'),
	path('transaction/', include('transaction.urls')),
	path('category/', include('category.urls')),
    path('admin/', admin.site.urls),
]
