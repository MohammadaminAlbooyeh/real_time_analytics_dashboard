from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from .models import Card, BOXES

class CardListView(ListView):
    model = Card
    template_name = 'cards/card_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        box_num = self.kwargs.get("box_num")
        if box_num is not None:
            queryset = queryset.filter(box=box_num)
        return queryset.order_by("date_created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_num"] = self.kwargs.get("box_num")
        return context

class CardCreateView(CreateView):
    model = Card
    fields = ["question", "answer", "box"]
    template_name = "cards/card_form.html"
    success_url = reverse_lazy("home") # Changed this line

class CardUpdateView(UpdateView):
    model = Card
    fields = ["question", "answer", "box"]
    template_name = "cards/card_form.html"
    success_url = reverse_lazy("home") # Changed this line

class CardDeleteView(DeleteView):
    model = Card
    template_name = "cards/card_confirm_delete.html"
    success_url = reverse_lazy("home") # Also change this for consistency, though it might not have caused an error yet

class BoxView(TemplateView):
    template_name = "cards/boxes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["boxes"] = BOXES
        return context