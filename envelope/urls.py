from django.urls import path
from .views import EnvelopeView, EnvelopeCreateView, EnvelopeUpdateView

urlpatterns = [
    path('', EnvelopeView.as_view(), name='envelope-list'),
    path('<int:year>/<int:month>/', EnvelopeView.as_view(), name='envelope-list'),
    path('envelope/update/<pk>/', EnvelopeUpdateView.as_view(), name='envelope-update'),
    path('envelope/create/<group_pk>/<cat_pk>/', EnvelopeCreateView.as_view(), name='envelope-create'),   
]