from django.urls import path
from .views import ForecastTemplateView

urlpatterns = [
    path('', ForecastTemplateView.as_view(), name='forecast-view'),
]
