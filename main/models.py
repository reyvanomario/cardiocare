from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Article(models.Model):
    TITLE_STYLE_CHOICES = [
        ('default', 'Gaya Default'),
        ('red-shadow', 'Bayangan Merah'),
    ]
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    publish_date = models.DateField()
    content = models.TextField(blank=True)
    source_url = models.URLField(max_length=500)

    def __str__(self):
        return self.title

