from django.contrib import admin
from django.urls import path, include

urlpatterns = [
	path('', include('account.urls')),
	path('budget/', include('budget.urls')),
	path('envelope/', include('envelope.urls')),
	path('forecast/', include('forecast.urls')),	
	path('transaction/', include('transaction.urls')),
	path('category/', include('category.urls')),
    path('admin/', admin.site.urls),
]
