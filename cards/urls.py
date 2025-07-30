from django.urls import path
from django.views.generic import TemplateView 
from .views import (
    CardCreateView,
    CardUpdateView,
    CardDeleteView,
    BoxView,
    CardListView,
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='cards/home.html'), name='home'), 
    path('new/', CardCreateView.as_view(), name='card-create'),
    path('<int:pk>/update/', CardUpdateView.as_view(), name='card-update'),
    path('<int:pk>/delete/', CardDeleteView.as_view(), name='card-delete'),
    path('boxes/', BoxView.as_view(), name='boxes'),
    path('boxes/<int:box_num>/', CardListView.as_view(), name='box-cards'),
]