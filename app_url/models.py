from django.db import models
from django.utils import timezone

class URL(models.Model):
    Original_Url=models.URLField()
    Short_Url=models.URLField()
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.Original_Url