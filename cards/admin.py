from django.contrib import admin

# Register your models here.
# flashcard_app/cards/admin.py

from .models import Card

admin.site.register(Card)