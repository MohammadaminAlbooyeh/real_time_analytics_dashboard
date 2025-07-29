from django.urls import path
from .views import (
    CardListView,
    CardCreateView,
    CardUpdateView,
    CardDeleteView
)

urlpatterns = [
    path('', CardListView.as_view(), name='card-list'),
    path('new/', CardCreateView.as_view(), name='card-create'),
    path('<int:pk>/update/', CardUpdateView.as_view(), name='card-update'),
    path('<int:pk>/delete/', CardDeleteView.as_view(), name='card-delete'),
]