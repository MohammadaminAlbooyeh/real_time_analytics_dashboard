from django.db import models

BOXES = (
    (1, "Box 1"),
    (2, "Box 2"),
    (3, "Box 3"),
)

class Card(models.Model):
    question = models.TextField()
    answer = models.TextField()
    box = models.IntegerField(default=BOXES[0][0], choices=BOXES)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Question: {self.question[:50]}{'...' if len(self.question) > 50 else ''} (Box: {self.box})"