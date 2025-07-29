# flashcard_app/cards/views.py

from django.urls import reverse_lazy 
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Card

class CardListView(ListView):
    model = Card
    queryset = Card.objects.all().order_by("date_created") 
    template_name = 'cards/card_list.html'

class CardCreateView(CreateView): 
    model = Card
    fields = ["question", "answer"]
    template_name = "cards/card_form.html" 
    success_url = reverse_lazy("card-list")

class CardUpdateView(UpdateView): 
    model = Card
    fields = ["question", "answer"]
    template_name = "cards/card_form.html" 
    success_url = reverse_lazy("card-list") 

class CardDeleteView(DeleteView): 
    model = Card
    template_name = "cards/card_confirm_delete.html" 
    success_url = reverse_lazy("card-list") 