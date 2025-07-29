# flashcard_app/cards/models.py

from django.db import models

class Card(models.Model):
    question = models.TextField()
    answer = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        
        return f"Question: {self.question[:50]}{'...' if len(self.question) > 50 else ''}"