from django.contrib import admin
from django.urls import path, include
from django.views.generic.list import ListView
from account.models import Account

urlpatterns = [
	path('', ListView.as_view(
		template_name='homepage.html', 
		model=Account,
		context_object_name = 'account_list',
		), name='homepage-index'),
	path('budget/', include('budget.urls')),
	path('forecast/', include('forecast.urls')),	
	path('transaction/', include('transaction.urls')),
	path('category/', include('category.urls')),
    path('admin/', admin.site.urls),
]
